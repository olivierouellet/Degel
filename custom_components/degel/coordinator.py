"""Data coordinator for Dégel."""

from __future__ import annotations

import logging
from datetime import datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import ThawApiError, ThawClient, ThawZone
from .const import (
    CONF_DAYS_AFTER,
    CONF_DAYS_BEFORE,
    CONF_ZONES,
    DEFAULT_DAYS_AFTER,
    DEFAULT_DAYS_BEFORE,
    DEFAULT_ZONES,
    DOMAIN,
    FETCH_INTERVAL,
)
from .season import transitions

_LOGGER = logging.getLogger(__name__)

type DegelConfigEntry = ConfigEntry[DegelCoordinator]


class DegelCoordinator(DataUpdateCoordinator[dict[int, ThawZone]]):
    """Fetches the thaw zones every few hours, and updates the entities when a period starts or ends."""

    config_entry: DegelConfigEntry

    def __init__(self, hass: HomeAssistant, entry: DegelConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=FETCH_INTERVAL,
        )
        self.client = ThawClient(async_get_clientsession(hass))
        self.zones: list[int] = sorted(int(z) for z in entry.options.get(CONF_ZONES, DEFAULT_ZONES))
        self.days_before: int = int(entry.options.get(CONF_DAYS_BEFORE, DEFAULT_DAYS_BEFORE))
        self.days_after: int = int(entry.options.get(CONF_DAYS_AFTER, DEFAULT_DAYS_AFTER))
        self._unsub_transition: CALLBACK_TYPE | None = None

    def selected(self) -> list[ThawZone]:
        """The followed zones the service published, by number."""
        data = self.data or {}
        return [data[z] for z in self.zones if z in data]

    async def _async_update_data(self) -> dict[int, ThawZone]:
        try:
            zones = await self.client.async_get_zones()
        except ThawApiError as err:
            if self.data is None:
                raise UpdateFailed(str(err)) from err
            # The dates rarely change: keep the last ones rather than make cards flicker.
            _LOGGER.warning("Could not refresh the thaw zones, keeping the last dates: %s", err)
            return self.data
        self._schedule_transition([zones[z] for z in self.zones if z in zones])
        return zones

    def _schedule_transition(self, zones: list[ThawZone]) -> None:
        """Wake up at the next start, end or window edge: polling alone would be up to 6 hours late."""
        self.cancel_transition()
        now = dt_util.utcnow()
        upcoming = [t for t in transitions(zones, self.days_before, self.days_after) if t > now]
        if upcoming:
            self._unsub_transition = async_track_point_in_utc_time(self.hass, self._async_transition, upcoming[0])

    @callback
    def _async_transition(self, _now: datetime) -> None:
        self._unsub_transition = None
        self.async_update_listeners()
        self._schedule_transition(self.selected())

    @callback
    def cancel_transition(self) -> None:
        if self._unsub_transition:
            self._unsub_transition()
            self._unsub_transition = None
