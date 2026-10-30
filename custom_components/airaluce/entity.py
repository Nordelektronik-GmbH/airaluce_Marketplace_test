"""Base entity for AVITANA aira luce platforms."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


class AiraLuceEntity(CoordinatorEntity):
    """Represent an entity backed by the AVITANA aira luce coordinator."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        api,
        unique_id_prefix: str,
        unique_id_suffix: str,
        name: str | None,
    ) -> None:
        """Initialize an AVITANA aira luce entity and its device information."""
        super().__init__(coordinator)
        self.api = api
        self._attr_unique_id = f"{unique_id_prefix}_{unique_id_suffix}"
        self._attr_name = name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id_prefix)},
            name=api.device_name,
            manufacturer=api.manufacturer,
            model=api.model,
            sw_version=api.sw_version,
            configuration_url=api.web_url,
        )
