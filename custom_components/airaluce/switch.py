"""Switch platform for AVITANA aira luce power control."""

from typing import Any, override

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import AiraLuceConfigEntry
from .entity import AiraLuceEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AiraLuceConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the AVITANA aira luce power switch."""
    runtime_data = entry.runtime_data
    async_add_entities(
        [
            AiraLucePowerSwitch(
                runtime_data.coordinator,
                runtime_data.api,
                runtime_data.unique_id_prefix,
            )
        ]
    )


class AiraLucePowerSwitch(AiraLuceEntity, SwitchEntity):
    """Control AVITANA aira luce master power."""

    def __init__(self, coordinator, api, unique_id_prefix: str) -> None:
        """Initialize the power switch."""
        super().__init__(coordinator, api, unique_id_prefix, "power", "Power")

    @property
    @override
    def is_on(self) -> bool:
        """Return whether AVITANA aira luce master power is on."""
        return int(self.coordinator.data.get("on", 0)) == 1

    @override
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on AVITANA aira luce master power."""
        await self.api.async_power_on()
        await self.coordinator.async_request_refresh()

    @override
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off AVITANA aira luce master power."""
        await self.api.async_power_off()
        await self.coordinator.async_request_refresh()
