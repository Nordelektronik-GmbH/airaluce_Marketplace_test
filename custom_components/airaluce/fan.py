"""Fan platform for AVITANA aira luce devices."""

from typing import Any, override

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import AiraLuceConfigEntry
from .entity import AiraLuceEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AiraLuceConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the AVITANA aira luce fan entity."""
    runtime_data = entry.runtime_data
    async_add_entities(
        [
            AiraLuceFan(
                runtime_data.coordinator,
                runtime_data.api,
                runtime_data.unique_id_prefix,
            )
        ]
    )


class AiraLuceFan(AiraLuceEntity, FanEntity):
    """Represent the AVITANA aira luce fan."""

    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
    )

    def __init__(self, coordinator, api, unique_id_prefix: str) -> None:
        """Initialize the fan entity."""
        super().__init__(coordinator, api, unique_id_prefix, "fan", "Fan")

    @property
    @override
    def is_on(self) -> bool:
        """Return whether master power is on and the fan has a speed set."""
        return (
            int(self.coordinator.data.get("on", 0)) == 1
            and int(self.coordinator.data.get("fan", 0)) > 0
        )

    @property
    @override
    def percentage(self) -> int:
        """Return the current fan speed as a percentage."""
        return round(int(self.coordinator.data.get("fan", 0)) * 100 / 255)

    @property
    @override
    def speed_count(self) -> int:
        """Return the number of supported fan speed levels."""
        return 4

    @override
    async def async_set_percentage(self, percentage: int) -> None:
        """Set fan speed to a percentage."""
        # 2026_10_02_CL: Changed: Maps percentage values to the five firmware levels.
        # Why: The firmware rounds PWM values to 0, 64, 128, 192, or 255.
        # Effect: HA fan levels correspond to off, 25, 50, 75, and 100 percent.
        # Old: The number control could send arbitrary intermediate values.
        raw_value = round(percentage * 255 / 100)
        await self.api.async_set_slider(value=raw_value)
        await self.coordinator.async_request_refresh()

    # 2026_10_05_CL: Changed: The fan handler also accepts the optional positional preset_mode parameter.
    # Why: Home Assistant may pass percentage and preset_mode positionally to async_turn_on.
    # Effect: fan.turn_on no longer raises TypeError when called with two arguments.
    # Old: The handler accepted only percentage as a positional argument.
    @override
    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan at the requested percentage."""
        await self.async_set_percentage(percentage if percentage is not None else 25)

    @override
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the fan."""
        await self.async_set_percentage(0)
