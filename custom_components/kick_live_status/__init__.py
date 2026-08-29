"""The Kick Live Status integration."""
import asyncio
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_STREAMERS, DEFAULT_SCAN_INTERVAL, DOMAIN, KICK_API_BASE_URL

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Kick Live Status from a config entry."""
    _LOGGER.info("Setting up Kick Live Status integration")

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

        results = await asyncio.gather(*(fetch_streamer(s) for s in streamers))

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

    # Store coordinator so diagnostics.py and sensor.py can access it
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading Kick Live Status integration")

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok