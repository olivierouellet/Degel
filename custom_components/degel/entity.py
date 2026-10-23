"""Common base for the Dégel entities."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import ThawZone
from .const import ATTRIBUTION, DOMAIN, INFO_URL
from .coordinator import DegelCoordinator


def zone_unique_id_prefix(entry: ConfigEntry, zone: int) -> str:
    return f"{entry.entry_id}_zone_{zone}_"


class DegelEntity(CoordinatorEntity[DegelCoordinator]):
    """One device for the whole service; entities for the season and for each followed zone."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: DegelCoordinator, key: str, zone: int | None = None) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._zone = zone
        if zone is None:
            self._attr_unique_id = f"{entry.entry_id}_{key}"
        else:
            self._attr_unique_id = f"{zone_unique_id_prefix(entry, zone)}{key}"
            self._attr_translation_placeholders = {"zone": str(zone)}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Dégel",
            manufacturer="Transports et Mobilité durable Québec",
            model="Zones de dégel",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=INFO_URL,
        )

    @property
    def zone(self) -> ThawZone | None:
        """This entity's zone, once published."""
        if self._zone is None or self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._zone)

    @property
    def available(self) -> bool:
        return super().available and (self._zone is None or self.zone is not None)
