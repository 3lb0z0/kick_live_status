"""Config flow for Kick Live Status integration."""
import logging
from typing import Any
import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_STREAMERS, DEFAULT_STREAMERS, OAUTH_TOKEN_URL

_LOGGER = logging.getLogger(__name__)

CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"


class KickLiveStatusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Kick Live Status."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return KickLiveStatusOptionsFlowHandler()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial setup step."""
        errors = {}

        if user_input is not None:
            client_id = user_input[CONF_CLIENT_ID].strip()
            client_secret = user_input[CONF_CLIENT_SECRET].strip()
            streamers_raw = user_input[CONF_STREAMERS]

            session = async_get_clientsession(self.hass)
            payload = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            try:
                async with session.post(
                    OAUTH_TOKEN_URL, data=payload, headers=headers
                ) as resp:
                    if resp.status == 200:
                        token_data = await resp.json()
                        streamers_list = [
                            s.strip().lower()
                            for s in streamers_raw.split(",")
                            if s.strip()
                        ]

                        return self.async_create_entry(
                            title="Kick Live Status",
                            data={
                                CONF_CLIENT_ID: client_id,
                                CONF_CLIENT_SECRET: client_secret,
                                CONF_STREAMERS: streamers_list,
                                "access_token": token_data.get("access_token"),
                            },
                        )
                    else:
                        errors["base"] = "invalid_auth"
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_CLIENT_ID): str,
                vol.Required(CONF_CLIENT_SECRET): str,
                vol.Required(
                    CONF_STREAMERS, default=", ".join(DEFAULT_STREAMERS)
                ): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )


class KickLiveStatusOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Kick Live Status options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the streamer list options."""
        if user_input is not None:
            streamers_list = [
                s.strip().lower()
                for s in user_input[CONF_STREAMERS].split(",")
                if s.strip()
            ]
            return self.async_create_entry(
                title="", data={CONF_STREAMERS: streamers_list}
            )

        # Access self.config_entry directly provided by HA base class
        current_streamers = self.config_entry.options.get(
            CONF_STREAMERS, self.config_entry.data.get(CONF_STREAMERS, [])
        )
        streamers_str = ", ".join(current_streamers)

        options_schema = vol.Schema(
            {
                vol.Required(CONF_STREAMERS, default=streamers_str): str,
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)