"""Sensor platform for AVITANA aira luce device state."""

from typing import override

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import AiraLuceConfigEntry
from .entity import AiraLuceEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AiraLuceConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up AVITANA aira luce state sensors."""
    runtime_data = entry.runtime_data
    coordinator = runtime_data.coordinator
    api = runtime_data.api
    unique_id_prefix = runtime_data.unique_id_prefix
    async_add_entities(
        [
            AiraLuceStateSensor(
                coordinator,
                api,
                unique_id_prefix,
                "brightness_top",
                "Brightness Top",
                "brightness",
            ),
            AiraLuceStateSensor(
                coordinator, api, unique_id_prefix, "color_top", "Color Top", "color"
            ),
            AiraLuceStateSensor(
                coordinator,
                api,
                unique_id_prefix,
                "brightness_bottom",
                "Brightness Bottom",
                "brightness_bottom",
            ),
            AiraLuceStateSensor(
                coordinator,
                api,
                unique_id_prefix,
                "color_bottom",
                "Color Bottom",
                "color_bottom",
            ),
        ]
    )


class AiraLuceStateSensor(AiraLuceEntity, SensorEntity):
    """Expose one AVITANA aira luce state value as a sensor."""

    def __init__(
        self,
        coordinator,
        api,
        unique_id_prefix: str,
        unique_id_suffix: str,
        name: str,
        state_key: str,
    ) -> None:
        """Initialize a sensor for one state key."""
        super().__init__(coordinator, api, unique_id_prefix, unique_id_suffix, name)
        self._state_key = state_key

    @property
    @override
    def native_value(self) -> int:
        """Return the current value for this sensor."""
        return int(self.coordinator.data.get(self._state_key, 0))
