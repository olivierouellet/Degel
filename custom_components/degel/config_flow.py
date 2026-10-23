"""Config and options flows for Dégel: the zones to follow, and how long before and after to show the card."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .api import ThawApiError, ThawClient
from .const import (
    CONF_DAYS_AFTER,
    CONF_DAYS_BEFORE,
    CONF_ZONES,
    DEFAULT_DAYS_AFTER,
    DEFAULT_DAYS_BEFORE,
    DEFAULT_ZONES,
    DOMAIN,
    MAX_DAYS,
    ZONES,
)

_LOGGER = logging.getLogger(__name__)


def _days_selector() -> NumberSelector:
    return NumberSelector(
        NumberSelectorConfig(min=0, max=MAX_DAYS, step=1, unit_of_measurement="d", mode=NumberSelectorMode.BOX)
    )


def _schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            # Options are strings: selector values and translation keys must be.
            vol.Required(CONF_ZONES, default=[str(z) for z in defaults[CONF_ZONES]]): SelectSelector(
                SelectSelectorConfig(
                    options=[str(z) for z in ZONES],
                    multiple=True,
                    mode=SelectSelectorMode.LIST,
                    translation_key="zone",
                )
            ),
            vol.Required(CONF_DAYS_BEFORE, default=defaults[CONF_DAYS_BEFORE]): _days_selector(),
            vol.Required(CONF_DAYS_AFTER, default=defaults[CONF_DAYS_AFTER]): _days_selector(),
        }
    )


def _options(user_input: dict[str, Any]) -> dict[str, Any]:
    return {
        CONF_ZONES: sorted(int(z) for z in user_input[CONF_ZONES]),
        CONF_DAYS_BEFORE: int(user_input[CONF_DAYS_BEFORE]),
        CONF_DAYS_AFTER: int(user_input[CONF_DAYS_AFTER]),
    }


class DegelConfigFlow(ConfigFlow, domain=DOMAIN):
    """Set up Dégel (once: a single entry follows any combination of zones)."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        client = ThawClient(async_get_clientsession(self.hass))
        if user_input is not None:
            if not user_input[CONF_ZONES]:
                errors[CONF_ZONES] = "no_zone"
            else:
                try:
                    await client.async_get_zones()
                except ThawApiError as err:
                    _LOGGER.warning("Could not load the thaw zones: %s", err)
                    errors["base"] = "cannot_connect"
                else:
                    return self.async_create_entry(title="Dégel", data={}, options=_options(user_input))

        defaults = {
            CONF_ZONES: await self._async_home_zones(client),
            CONF_DAYS_BEFORE: DEFAULT_DAYS_BEFORE,
            CONF_DAYS_AFTER: DEFAULT_DAYS_AFTER,
        }
        if user_input is not None:
            defaults = {**defaults, **user_input}
        return self.async_show_form(step_id="user", data_schema=_schema(defaults), errors=errors)

    async def _async_home_zones(self, client: ThawClient) -> list[int]:
        """The zone of the Home Assistant home location, when it is in one."""
        try:
            zone = await client.async_zone_at(self.hass.config.latitude, self.hass.config.longitude)
        except ThawApiError as err:
            _LOGGER.debug("Could not find the zone of the home location: %s", err)
            return DEFAULT_ZONES
        return [zone] if zone else DEFAULT_ZONES

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> DegelOptionsFlow:
        return DegelOptionsFlow()


class DegelOptionsFlow(OptionsFlow):
    """Change the zones or the window around the thaw periods."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            if user_input[CONF_ZONES]:
                return self.async_create_entry(data=_options(user_input))
            errors[CONF_ZONES] = "no_zone"

        options = self.config_entry.options
        defaults = {
            CONF_ZONES: options.get(CONF_ZONES, DEFAULT_ZONES),
            CONF_DAYS_BEFORE: options.get(CONF_DAYS_BEFORE, DEFAULT_DAYS_BEFORE),
            CONF_DAYS_AFTER: options.get(CONF_DAYS_AFTER, DEFAULT_DAYS_AFTER),
        }
        if user_input is not None:
            defaults = {**defaults, **user_input}
        return self.async_show_form(step_id="init", data_schema=_schema(defaults), errors=errors)
