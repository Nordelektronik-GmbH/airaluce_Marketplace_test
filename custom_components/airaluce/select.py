"""Select platform for choosing AVITANA aira luce lighting zones."""

from typing import override

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import AiraLuceConfigEntry
from .entity import AiraLuceEntity

_ZONE_TO_SELECTION = {
    "Top": 1,
    "Bottom": 2,
    "Top+Bottom": 3,
}
_SELECTION_TO_ZONE = {v: k for k, v in _ZONE_TO_SELECTION.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AiraLuceConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the AVITANA aira luce zone selector."""
    runtime_data = entry.runtime_data
    async_add_entities(
        [
            AiraLuceZoneSelect(
                runtime_data.coordinator,
                runtime_data.api,
                runtime_data.unique_id_prefix,
            )
        ]
    )


class AiraLuceZoneSelect(AiraLuceEntity, SelectEntity):
    """Select which AVITANA aira luce lighting zone to control."""

    _attr_options = ["Top", "Bottom", "Top+Bottom"]

    def __init__(self, coordinator, api, unique_id_prefix: str) -> None:
        """Initialize the zone selector."""
        super().__init__(coordinator, api, unique_id_prefix, "zone", "Zone")

    @property
    @override
    def current_option(self) -> str | None:
        """Return the currently selected lighting zone."""
        selection = int(self.coordinator.data.get("selection", 3))
        return _SELECTION_TO_ZONE.get(selection, "Top+Bottom")

    @override
    async def async_select_option(self, option: str) -> None:
        """Select a lighting zone."""
        selection = _ZONE_TO_SELECTION.get(option, 3)
        await self.api.async_set_selection(selection)
        await self.coordinator.async_request_refresh()
