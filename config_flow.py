"""Config flow for Telekom Glasfaser Modem 1."""

import ipaddress

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DEFAULT_HOST, DOMAIN, SCAN_INTERVAL_SECONDS
from .ont_status import OntClient, OntError


class TelekomOntConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TelekomOntOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            host = user_input["host"].strip()
            try:
                ipaddress.ip_address(host)
            except ValueError:
                errors["base"] = "invalid_host"
            else:
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()
                try:
                    client = OntClient(async_get_clientsession(self.hass), host)
                    await client.async_get_status()
                except OntError:
                    errors["base"] = "cannot_connect"
                else:
                    return self.async_create_entry(
                        title=f"Telekom Glasfaser Modem 1 ({host})",
                        data={"host": host},
                    )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required("host", default=DEFAULT_HOST): str}
            ),
            errors=errors,
        )


class TelekomOntOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "scan_interval",
                        default=self.config_entry.options.get(
                            "scan_interval", SCAN_INTERVAL_SECONDS
                        ),
                    ): int
                }
            ),
        )

