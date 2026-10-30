"""The AVITANA aira luce integration."""

from dataclasses import dataclass

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import PLATFORMS
from .coordinator import AiraLuceApi, AiraLuceCoordinator


@dataclass(slots=True)
class AiraLuceRuntimeData:
    """Data associated with one configured AVITANA aira luce device."""

    api: AiraLuceApi
    coordinator: AiraLuceCoordinator
    unique_id_prefix: str


type AiraLuceConfigEntry = ConfigEntry[AiraLuceRuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: AiraLuceConfigEntry) -> bool:
    """Set up an AVITANA aira luce config entry."""
    api = AiraLuceApi(hass, entry.data)
    try:
        info = await api.async_get_info()
    except (TimeoutError, aiohttp.ClientError) as err:
        raise ConfigEntryNotReady(
            "Unable to connect to the AVITANA aira luce device"
        ) from err
    api.manufacturer = info.get("manufacturer")
    api.model = info.get("model")
    api.sw_version = info.get("sw_version")
    api.web_url = info.get("web_url", api.web_url)
    coordinator = AiraLuceCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()

    # 2026_10_19_CL: Changed: Store per-entry objects in typed runtime data.
    # Why: Home Assistant requires ConfigEntry.runtime_data instead of a hass.data registry.
    # Effect: Platforms read their API and coordinator from the owning config entry.
    # Old: Runtime objects were stored in hass.data[DOMAIN][entry.entry_id].
    entry.runtime_data = AiraLuceRuntimeData(
        api=api,
        coordinator=coordinator,
        unique_id_prefix=entry.unique_id or entry.entry_id,
    )

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: AiraLuceConfigEntry) -> bool:
    """Unload an AVITANA aira luce config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
