"""Tests for the AVITANA aira luce config flow."""

from ipaddress import ip_address

import aiohttp
import pytest

from homeassistant.components.airaluce.const import DOMAIN
from homeassistant.config_entries import SOURCE_USER, SOURCE_ZEROCONF
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from tests.common import MockConfigEntry
from tests.test_util.aiohttp import AiohttpClientMocker

API_INFO = {
    "unique_id": "airaluce_123456",
    "device": "Living room",
    "web_url": "http://192.0.2.10/",
    "api_base": "http://192.0.2.10/api",
}


def _zeroconf_info() -> ZeroconfServiceInfo:
    address = ip_address("192.0.2.10")
    return ZeroconfServiceInfo(
        ip_address=address,
        ip_addresses=[address],
        port=80,
        hostname="airaluce.local.",
        type="_airaluce._tcp.local.",
        name="AiraLuce._airaluce._tcp.local.",
        properties={},
    )


@pytest.mark.parametrize(
    ("device_info", "expected_title"),
    [
        pytest.param(API_INFO, "Living room", id="custom_device_name"),
        pytest.param(
            API_INFO | {"device": "AVITANA aira luce"},
            "AVITANA aira luce",
            id="product_device_name",
        ),
        pytest.param(
            {
                "unique_id": "airaluce_123456",
                "web_url": "http://192.0.2.10/",
                "api_base": "http://192.0.2.10/api",
            },
            "AVITANA aira luce",
            id="default_device_name",
        ),
    ],
)
async def test_user_flow_creates_entry(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    device_info: dict[str, str],
    expected_title: str,
) -> None:
    """Create an entry through the manual setup flow."""
    aioclient_mock.get("http://192.0.2.10:80/api/info", json=device_info)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: "192.0.2.10", CONF_PORT: 80},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == expected_title
    assert result["data"]["device_name"] == expected_title
    assert result["data"]["unique_id"] == "airaluce_123456"
    assert result["data"]["web_url"] == "http://192.0.2.10/"
    assert result["data"]["api_base"] == "http://192.0.2.10/api"


async def test_user_flow_recovers_after_server_error(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Allow setup to continue after correcting the host following a server error."""
    aioclient_mock.get("http://192.0.2.10:80/api/info", status=500)
    retry_info = API_INFO | {
        "web_url": "http://192.0.2.11/",
        "api_base": "http://192.0.2.11/api",
    }
    aioclient_mock.get("http://192.0.2.11:80/api/info", json=retry_info)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: "192.0.2.10", CONF_PORT: 80},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: "192.0.2.11", CONF_PORT: 80},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["web_url"] == "http://192.0.2.11/"


async def test_user_flow_recovers_after_connection_failure(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Allow setup to continue after correcting the host."""
    aioclient_mock.get("http://192.0.2.10:80/api/info", exc=aiohttp.ClientError())
    retry_info = API_INFO | {
        "web_url": "http://192.0.2.11/",
        "api_base": "http://192.0.2.11/api",
    }
    aioclient_mock.get("http://192.0.2.11:80/api/info", json=retry_info)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: "192.0.2.10", CONF_PORT: 80},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: "192.0.2.11", CONF_PORT: 80},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Living room"
    assert result["data"]["web_url"] == "http://192.0.2.11/"


@pytest.mark.parametrize(
    "info",
    [
        {},
        {"unique_id": None},
        {"unique_id": ""},
        {"unique_id": "   "},
        {"unique_id": 123},
    ],
)
async def test_user_flow_recovers_after_invalid_unique_id(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, info: dict[str, object]
) -> None:
    """Allow setup to continue after entering a host with a valid device ID."""
    aioclient_mock.get("http://192.0.2.10:80/api/info", json=info)
    retry_info = API_INFO | {
        "web_url": "http://192.0.2.11/",
        "api_base": "http://192.0.2.11/api",
    }
    aioclient_mock.get("http://192.0.2.11:80/api/info", json=retry_info)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: "192.0.2.10", CONF_PORT: 80},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_unique_id"}

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: "192.0.2.11", CONF_PORT: 80},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["unique_id"] == API_INFO["unique_id"]


async def test_user_flow_aborts_for_configured_device(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Abort setup when the device is already configured."""
    existing_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=API_INFO["unique_id"],
        data={},
    )
    existing_entry.add_to_hass(hass)
    aioclient_mock.get("http://192.0.2.10:80/api/info", json=API_INFO)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: "192.0.2.10", CONF_PORT: 80},
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_zeroconf_flow_confirms_discovered_device(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Confirm a valid device discovered through Zeroconf."""
    aioclient_mock.get("http://192.0.2.10:80/api/info", json=API_INFO)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=_zeroconf_info(),
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "confirm"
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["unique_id"] == API_INFO["unique_id"]


async def test_zeroconf_flow_aborts_for_configured_device(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Abort discovery when the device is already configured."""
    existing_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=API_INFO["unique_id"],
        data={},
    )
    existing_entry.add_to_hass(hass)
    aioclient_mock.get("http://192.0.2.10:80/api/info", json=API_INFO)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=_zeroconf_info(),
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
