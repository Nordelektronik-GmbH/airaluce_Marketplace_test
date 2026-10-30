"""Config flow for the AVITANA aira luce integration."""

from typing import Any, override

import aiohttp
from aiohttp import ClientTimeout
import probatio

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_UNIQUE_ID
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .const import CONF_API_BASE, CONF_DEVICE_NAME, CONF_WEB_URL, DEFAULT_PORT, DOMAIN


class AiraLuceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle configuration flows for AVITANA aira luce devices."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery: dict[str, Any] = {}

    async def _fetch_info(self, host: str, port: int) -> dict[str, Any]:
        session = async_get_clientsession(self.hass)
        url = f"http://{host}:{port}/api/info"
        async with session.get(url, timeout=ClientTimeout(total=8)) as resp:
            resp.raise_for_status()
            return await resp.json()

    @override
    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Set up a device discovered through Zeroconf."""
        host = discovery_info.host
        port = discovery_info.port or DEFAULT_PORT

        try:
            info = await self._fetch_info(host, port)
        # 2026_10_19_CL: Changed: Handle only expected HTTP client and timeout errors as connection failures.
        # Why: Unexpected exceptions indicate programming errors and should propagate.
        # Effect: Expected connection failures receive the appropriate user-facing response without masking unrelated errors.
        # Old: All exceptions were treated as connection failures.
        except (aiohttp.ClientError, TimeoutError):
            return self.async_abort(reason="cannot_connect")

        unique_id = info.get("unique_id")
        if not isinstance(unique_id, str) or not unique_id.strip():
            return self.async_abort(reason="invalid_unique_id")
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        self._discovery = {
            CONF_HOST: host,
            CONF_PORT: port,
            CONF_UNIQUE_ID: unique_id,
            CONF_DEVICE_NAME: info.get("device", "AVITANA aira luce"),
            CONF_WEB_URL: info.get("web_url", f"http://{host}:{port}"),
            CONF_API_BASE: info.get("api_base", f"http://{host}:{port}"),
        }

        self.context["title_placeholders"] = {"name": self._discovery[CONF_DEVICE_NAME]}
        return await self.async_step_confirm()

    @override
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Set up a device using manually entered connection details."""
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            try:
                info = await self._fetch_info(host, port)
            # 2026_10_19_CL: Changed: Handle only expected HTTP client and timeout errors as connection failures.
            # Why: Unexpected exceptions indicate programming errors and should propagate.
            # Effect: Expected connection failures receive the appropriate user-facing response without masking unrelated errors.
            # Old: All exceptions were treated as connection failures.
            except (aiohttp.ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            else:
                unique_id = info.get("unique_id")
                if not isinstance(unique_id, str) or not unique_id.strip():
                    errors["base"] = "invalid_unique_id"
                    return self.async_show_form(
                        step_id="user",
                        data_schema=probatio.Schema(
                            {
                                probatio.Required(CONF_HOST): str,
                                probatio.Required(CONF_PORT, default=DEFAULT_PORT): int,
                            }
                        ),
                        errors=errors,
                    )
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                data = {
                    CONF_HOST: host,
                    CONF_PORT: port,
                    CONF_UNIQUE_ID: unique_id,
                    CONF_DEVICE_NAME: info.get("device", "AVITANA aira luce"),
                    CONF_WEB_URL: info.get("web_url", f"http://{host}:{port}"),
                    CONF_API_BASE: info.get("api_base", f"http://{host}:{port}"),
                }
                return self.async_create_entry(title=data[CONF_DEVICE_NAME], data=data)

        schema = probatio.Schema(
            {
                probatio.Required(CONF_HOST): str,
                probatio.Required(CONF_PORT, default=DEFAULT_PORT): int,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm setup of a discovered device."""
        if user_input is not None:
            title = self._discovery.get(CONF_DEVICE_NAME, "AVITANA aira luce")
            return self.async_create_entry(title=title, data=self._discovery)

        return self.async_show_form(step_id="confirm")
