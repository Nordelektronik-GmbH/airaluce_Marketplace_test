"""API client and state coordinator for AVITANA aira luce."""

from collections.abc import Mapping
from datetime import timedelta
import logging
from typing import TYPE_CHECKING, Any, override

from aiohttp import ClientSession, ClientTimeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import SCAN_INTERVAL_SECONDS

if TYPE_CHECKING:
    from . import AiraLuceConfigEntry

_LOGGER = logging.getLogger(__name__)


class AiraLuceApi:
    """Client for the AVITANA aira luce firmware API."""

    def __init__(self, hass: HomeAssistant, config: Mapping[str, Any]) -> None:
        """Initialize the API client."""
        self._session: ClientSession = async_get_clientsession(hass)
        host = config["host"]
        port = int(config.get("port", 80))
        self.base_url = f"http://{host}:{port}"
        self.device_name = config.get("device_name", "AVITANA aira luce")
        self.manufacturer: str | None = None
        self.model: str | None = None
        self.sw_version: str | None = None
        self.web_url = config.get("web_url", self.base_url)
        self.supports_selection = True

    async def _get_json(self, path: str) -> dict[str, Any]:
        async with self._session.get(
            f"{self.base_url}{path}", timeout=ClientTimeout(total=8)
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def _get_text(self, path: str) -> str:
        async with self._session.get(
            f"{self.base_url}{path}", timeout=ClientTimeout(total=8)
        ) as resp:
            resp.raise_for_status()
            return await resp.text()

    async def async_get_info(self) -> dict[str, Any]:
        """Fetch device information from the firmware."""
        return await self._get_json("/api/info")

    async def async_get_state(self) -> dict[str, Any]:
        """Fetch the current device state."""
        return await self._get_json("/state")

    async def async_power_on(self) -> None:
        """Turn the device on."""
        await self._get_text("/button1")

    async def async_power_off(self) -> None:
        """Turn the device off."""
        await self._get_text("/button2")

    async def async_set_selection(self, selection: int) -> None:
        """Set the active lighting zone."""
        await self._get_text(f"/setSelection?selection={selection}")

    async def async_set_slider(self, **params: int) -> None:
        """Send slider values to the firmware."""
        if not params:
            return
        query = "&".join(f"{key}={int(value)}" for key, value in params.items())
        await self._get_text(f"/slider?{query}")


class AiraLuceCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate state updates from the device."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: AiraLuceConfigEntry,
        api: AiraLuceApi,
    ) -> None:
        """Initialize the state coordinator."""
        self.api = api
        super().__init__(
            hass,
            logger=_LOGGER,
            name="airaluce_state",
            config_entry=config_entry,
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )

    @override
    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.api.async_get_state()
        except Exception as err:
            raise UpdateFailed(f"AVITANA aira luce update failed: {err}") from err
