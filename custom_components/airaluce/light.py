"""Light platform for AVITANA aira luce devices."""

from typing import Any, override

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ColorMode,
    LightEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import AiraLuceConfigEntry
from .entity import AiraLuceEntity

# 2026_10_04_CL: Changed: Adjusted the Kelvin limits from yellow-white to blue-white.
# Why: The native HA picker derives its gradient from the Kelvin limits; 6500 K should remain white at the midpoint.
# Effect: The warm and cool ends appear brighter/yellower and bluer, respectively.
# Old: 2700-6500 K showed orange at the warm end and white at the cool end.
_MIN_COLOR_TEMP_KELVIN = 4000
_MAX_COLOR_TEMP_KELVIN = 9000


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AiraLuceConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the AVITANA aira luce light entity."""
    runtime_data = entry.runtime_data
    async_add_entities(
        [
            AiraLuceLight(
                runtime_data.coordinator,
                runtime_data.api,
                runtime_data.unique_id_prefix,
            )
        ]
    )


class AiraLuceLight(AiraLuceEntity, LightEntity):
    """Represent the AVITANA aira luce light and its color temperature."""

    _attr_name = None
    _attr_supported_color_modes = {ColorMode.COLOR_TEMP}
    _attr_min_color_temp_kelvin = _MIN_COLOR_TEMP_KELVIN
    _attr_max_color_temp_kelvin = _MAX_COLOR_TEMP_KELVIN

    def __init__(self, coordinator, api, unique_id_prefix: str) -> None:
        """Initialize the light entity."""
        super().__init__(coordinator, api, unique_id_prefix, "light", None)

    @property
    @override
    def color_mode(self) -> ColorMode:
        """Return the supported color mode."""
        return ColorMode.COLOR_TEMP

    @property
    @override
    def is_on(self) -> bool:
        """Return whether the selected light zone is on."""
        # 2026_10_03_CL: Changed: Light on-state uses master status and zone brightness.
        # Why: /state returns on as the 0/1 master status, not as a lamp-zone bitmask.
        # Effect: HA shows the light as off at brightness 0, even if the master remains on.
        # Old: The boolean on value was incorrectly combined with zone bitmasks.
        if int(self.coordinator.data.get("on", 0)) != 1:
            return False

        selection = int(self.coordinator.data.get("selection", 3))
        if selection == 1:
            return int(self.coordinator.data.get("brightness", 0)) > 0
        if selection == 2:
            return int(self.coordinator.data.get("brightness_bottom", 0)) > 0
        return any(
            int(self.coordinator.data.get(key, 0)) > 0
            for key in ("brightness", "brightness_bottom")
        )

    @property
    @override
    def brightness(self) -> int:
        """Return the brightness of the selected light zone."""
        return self._selected_value("brightness", "brightness_bottom")

    @property
    @override
    def color_temp_kelvin(self) -> int:
        """Return the color temperature of the selected light zone."""
        raw_color = self._selected_value("color", "color_bottom")
        # 2026_10_04_CL: Changed: Inverts the firmware color value when mapping it to HA Kelvin.
        # Why: Observed hardware color behavior is inverted relative to the previous raw-value assumption.
        # Effect: Cool/blue stays at the cool HA end and warm/yellow at the warm end.
        # Old: Raw value 0 was interpreted as cool and 255 as warm.
        return self._raw_color_to_kelvin(raw_color)

    def _selected_value(self, top_key: str, bottom_key: str) -> int:
        selection = int(self.coordinator.data.get("selection", 3))
        if selection in {2, 3}:
            return int(self.coordinator.data.get(bottom_key, 0))
        return int(self.coordinator.data.get(top_key, 0))

    @staticmethod
    def _raw_color_to_kelvin(raw_color: int) -> int:
        bounded_color = max(0, min(255, raw_color))
        return round(
            _MIN_COLOR_TEMP_KELVIN
            + (bounded_color / 255) * (_MAX_COLOR_TEMP_KELVIN - _MIN_COLOR_TEMP_KELVIN)
        )

    @staticmethod
    def _kelvin_to_raw_color(kelvin: int) -> int:
        bounded_kelvin = max(
            _MIN_COLOR_TEMP_KELVIN,
            min(_MAX_COLOR_TEMP_KELVIN, kelvin),
        )
        cold_fraction = (bounded_kelvin - _MIN_COLOR_TEMP_KELVIN) / (
            _MAX_COLOR_TEMP_KELVIN - _MIN_COLOR_TEMP_KELVIN
        )
        return round(cold_fraction * 255)

    def _zone_params(self, top_key: str, bottom_key: str, value: int) -> dict[str, int]:
        selection = int(self.coordinator.data.get("selection", 3))
        if selection == 1:
            return {top_key: value}
        if selection == 2:
            return {bottom_key: value}
        return {top_key: value, bottom_key: value}

    @override
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the selected light zone with the requested settings."""
        params: dict[str, int] = {}
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        if brightness is None:
            """brightness = self.brightness or 255 (olt: 255 ==> 100 % by turn_on and 26 ==> 10 % by default)"""
            brightness = self.brightness or 26
        params.update(
            self._zone_params("brightness", "brightness_bottom", int(brightness))
        )

        color_temp_kelvin = kwargs.get(ATTR_COLOR_TEMP_KELVIN)
        if color_temp_kelvin is not None:
            raw_color = self._kelvin_to_raw_color(int(color_temp_kelvin))
            params.update(self._zone_params("color", "color_bottom", raw_color))

        await self.api.async_set_slider(**params)
        await self.coordinator.async_request_refresh()

    @override
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the selected light zone."""
        params = self._zone_params("brightness", "brightness_bottom", 0)
        await self.api.async_set_slider(**params)
        await self.coordinator.async_request_refresh()
