"""Sensors for Dégel: start and end of each followed zone's thaw period."""

from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import DegelConfigEntry, DegelCoordinator
from .entity import DegelEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: DegelConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the start and end sensors of each followed zone."""
    coordinator = entry.runtime_data
    async_add_entities(
        sensor
        for zone in coordinator.zones
        for sensor in (ThawDateSensor(coordinator, zone, "start"), ThawDateSensor(coordinator, zone, "end"))
    )


class ThawDateSensor(DegelEntity, SensorEntity):
    """When a zone's thaw period starts or ends (the published time: 00:01 and 23:59)."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator: DegelCoordinator, zone: int, which: str) -> None:
        super().__init__(coordinator, which, zone)
        self._which = which
        self._attr_translation_key = which
        self._attr_icon = "mdi:calendar-start" if which == "start" else "mdi:calendar-end"

    @property
    def native_value(self) -> datetime | None:
        zone = self.zone
        if zone is None:
            return None
        return zone.start if self._which == "start" else zone.end
