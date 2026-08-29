"""Sensor platform for Kick Live Status integration."""
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import CONF_STREAMERS, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Kick Live Status sensors based on a config entry."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    streamers = entry.options.get(CONF_STREAMERS, entry.data.get(CONF_STREAMERS, []))

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

        # Display name shown in UI cards (e.g., "nickwhite")
        self._attr_name = streamer

        # Unique ID for Home Assistant registry
        self._attr_unique_id = f"kick_live_status_{streamer.lower()}"

        # Explicit entity ID format (e.g., "sensor.kick_nickwhite")
        self.entity_id = f"sensor.kick_{streamer.lower()}"

    @property
    def icon(self) -> str:
        """Return dynamic MDI icon depending on live state."""
        channel_data = self.coordinator.data.get(self._streamer, {})
        stream_info = channel_data.get("stream", {})
        if isinstance(stream_info, dict) and stream_info.get("is_live"):
            return "mdi:television-play"
        return "mdi:television-off"

    @property
    def entity_picture(self) -> str | None:
        """Return the live stream preview thumbnail if online."""
        channel_data = self.coordinator.data.get(self._streamer, {})
        stream_info = channel_data.get("stream", {})

        if isinstance(stream_info, dict) and stream_info.get("is_live"):
            thumbnail = stream_info.get("thumbnail")
            if thumbnail:
                return thumbnail

        # Returning None forces Home Assistant to fall back to self.icon
        return None

    @property
    def native_value(self) -> str:
        """Return 'live' or 'offline' based on stream payload."""
        channel_data = self.coordinator.data.get(self._streamer, {})
        stream_info = channel_data.get("stream", {})
        if isinstance(stream_info, dict) and stream_info.get("is_live"):
            return "live"
        return "offline"

    @property
    def extra_state_attributes(self) -> dict[str, str | int | None]:
        """Return stream title, category, viewer count, start time, thumbnail, and streamer name."""
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
            "thumbnail_url": (
                stream_info.get("thumbnail")
                if isinstance(stream_info, dict) and is_live
                else None
            ),
        }