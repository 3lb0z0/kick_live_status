"""Sensor platform for Kick Live Status integration."""
import asyncio
from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import CONF_STREAMERS, DEFAULT_SCAN_INTERVAL, DOMAIN, KICK_API_BASE_URL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Kick Live Status sensors based on a config entry."""
    streamers = entry.options.get(CONF_STREAMERS, entry.data.get(CONF_STREAMERS, []))
    client_id = entry.data.get("client_id")
    access_token = entry.data.get("access_token")

    async def async_update_data():
        """Fetch updated channel data from Kick API concurrently in parallel."""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Client-ID": client_id,
            "Accept": "application/json",
        }
        client_session = async_get_clientsession(hass)

        async def fetch_streamer(streamer: str):
            url = f"{KICK_API_BASE_URL}/channels?slug={streamer}"
            try:
                async with client_session.get(url, headers=headers) as response:
                    if response.status == 200:
                        payload = await response.json()
                        channels = payload.get("data", [])
                        if channels:
                            return streamer, channels[0]
                    else:
                        _LOGGER.warning(
                            "Failed to fetch data for %s: Status %s",
                            streamer,
                            response.status,
                        )
            except Exception as err:
                _LOGGER.error("Error updating Kick streamer %s: %s", streamer, err)
            return streamer, None

        # Execute all HTTP fetches in parallel
        results = await asyncio.gather(*(fetch_streamer(s) for s in streamers))

        # Build final data dictionary
        return {
            streamer: channel_data
            for streamer, channel_data in results
            if channel_data is not None
        }

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Kick Live Status Coordinator",
        update_method=async_update_data,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()

    entities = [
        KickStreamerSensor(coordinator, streamer) for streamer in streamers
    ]
    async_add_entities(entities, True)


class KickStreamerSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Kick Streamer Live Sensor."""

    def __init__(self, coordinator: DataUpdateCoordinator, streamer: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._streamer = streamer

        # Display name shown in UI cards (e.g., "iceposeidon")
        self._attr_name = streamer

        # Unique ID for Home Assistant registry
        self._attr_unique_id = f"kick_live_status_{streamer.lower()}"

        # Explicit entity ID format (e.g., "sensor.kick_iceposeidon")
        self.entity_id = f"sensor.kick_{streamer.lower()}"

        self._attr_icon = "mdi:television-play"

    @property
    def native_value(self) -> str:
        """Return 'live' or 'offline' based on stream payload."""
        channel_data = self.coordinator.data.get(self._streamer, {})
        stream_info = channel_data.get("stream", {})
        if stream_info and stream_info.get("is_live"):
            return "live"
        return "offline"

    @property
    def extra_state_attributes(self) -> dict[str, str | int | None]:
        """Return stream title, category, viewer count, start time, and streamer name."""
        channel_data = self.coordinator.data.get(self._streamer, {})
        stream_info = channel_data.get("stream", {})
        category_info = channel_data.get("category", {})

        is_live = (
            stream_info.get("is_live", False)
            if isinstance(stream_info, dict)
            else False
        )

        return {
            "streamer": self._streamer,
            "stream_title": channel_data.get("stream_title") if is_live else None,
            "category": (
                category_info.get("name")
                if isinstance(category_info, dict) and is_live
                else None
            ),
            "viewer_count": (
                stream_info.get("viewer_count", 0)
                if isinstance(stream_info, dict) and is_live
                else 0
            ),
            "start_time": (
                stream_info.get("start_time")
                if isinstance(stream_info, dict) and is_live
                else None
            ),
        }