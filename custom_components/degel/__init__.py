"""Dégel: Québec's spring thaw periods (périodes de dégel) for Home Assistant."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .coordinator import DegelConfigEntry, DegelCoordinator
from .entity import zone_unique_id_prefix

PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: DegelConfigEntry) -> bool:
    """Set up Dégel from a config entry."""
    coordinator = DegelCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    entry.async_on_unload(coordinator.cancel_transition)

    _remove_unfollowed_zones(hass, entry, coordinator.zones)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DegelConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload(hass: HomeAssistant, entry: DegelConfigEntry) -> None:
    """Reload when the zones or the window change."""
    await hass.config_entries.async_reload(entry.entry_id)


def _remove_unfollowed_zones(hass: HomeAssistant, entry: DegelConfigEntry, zones: list[int]) -> None:
    """Drop the entities of zones taken out in the options, rather than leave them unavailable."""
    registry = er.async_get(hass)
    kept = tuple(zone_unique_id_prefix(entry, z) for z in zones)
    for entity in er.async_entries_for_config_entry(registry, entry.entry_id):
        if "_zone_" in entity.unique_id and not entity.unique_id.startswith(kept):
            registry.async_remove(entity.entity_id)
