"""Binary sensors for Dégel: the season around the followed zones, and each zone's thaw period."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .api import ThawZone
from .coordinator import DegelConfigEntry, DegelCoordinator
from .entity import DegelEntity
from .season import ACTIVE, in_season, status, window


async def async_setup_entry(
    hass: HomeAssistant, entry: DegelConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the season sensor and one thaw period sensor per followed zone."""
    coordinator = entry.runtime_data
    async_add_entities(
        [ThawSeasonSensor(coordinator), *(ThawPeriodSensor(coordinator, zone) for zone in coordinator.zones)]
    )


def zone_attributes(zone: ThawZone, now: datetime) -> dict[str, Any]:
    return {
        "zone": zone.number,
        "name": zone.name,
        "start": zone.start.isoformat(),
        "end": zone.end.isoformat(),
        "status": status(zone, now),
    }


class ThawSeasonSensor(DegelEntity, BinarySensorEntity):
    """On from some days before the first followed thaw period starts until some days after the last one ends.

    Meant for card visibility; the Dégel card reads its `thaw_zones` attribute.
    """

    _attr_translation_key = "season"
    _attr_icon = "mdi:snowflake-melt"

    def __init__(self, coordinator: DegelCoordinator) -> None:
        super().__init__(coordinator, "season")

    @property
    def is_on(self) -> bool:
        c = self.coordinator
        return in_season(c.selected(), dt_util.utcnow(), c.days_before, c.days_after)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        c = self.coordinator
        now = dt_util.utcnow()
        zones = c.selected()
        attrs: dict[str, Any] = {
            "thaw_zones": [zone_attributes(z, now) for z in zones],
            "days_before": c.days_before,
            "days_after": c.days_after,
            "active_zones": [z.number for z in zones if status(z, now) == ACTIVE],
        }
        if zones:
            windows = [window(z, c.days_before, c.days_after) for z in zones]
            attrs["season_start"] = min(w[0] for w in windows).isoformat()
            attrs["season_end"] = max(w[1] for w in windows).isoformat()
        return attrs


class ThawPeriodSensor(DegelEntity, BinarySensorEntity):
    """On during one zone's thaw period, when load restrictions apply."""

    _attr_translation_key = "thaw_period"
    _attr_icon = "mdi:truck-alert"

    def __init__(self, coordinator: DegelCoordinator, zone: int) -> None:
        super().__init__(coordinator, "thaw_period", zone)

    @property
    def is_on(self) -> bool | None:
        zone = self.zone
        return status(zone, dt_util.utcnow()) == ACTIVE if zone else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        zone = self.zone
        return zone_attributes(zone, dt_util.utcnow()) if zone else {}
