"""Tests for the AVITANA aira luce API client and coordinator."""

import asyncio
from typing import Any
from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

from homeassistant.components.airaluce.const import DOMAIN
from homeassistant.components.airaluce.coordinator import (
    AiraLuceApi,
    AiraLuceCoordinator,
)
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from tests.common import MockConfigEntry
from tests.test_util.aiohttp import AiohttpClientMocker


def _config_entry(hass: HomeAssistant) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="airaluce-test",
        data={CONF_HOST: "192.0.2.10", CONF_PORT: 80},
    )
    entry.add_to_hass(hass)
    return entry


@pytest.mark.parametrize(
    ("path", "method_name", "payload"),
    [
        ("/api/info", "async_get_info", {"unique_id": "airaluce-123"}),
        ("/state", "async_get_state", {"state": "on"}),
    ],
)
async def test_api_gets_json_from_firmware(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    path: str,
    method_name: str,
    payload: dict[str, str],
) -> None:
    """Return JSON from the requested firmware endpoint."""
    aioclient_mock.get(f"http://192.0.2.10:80{path}", json=payload)
    api = AiraLuceApi(hass, {CONF_HOST: "192.0.2.10", CONF_PORT: 80})

    assert await getattr(api, method_name)() == payload


async def test_coordinator_returns_state_from_firmware(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Return the state provided by the firmware."""
    state = {"power": True}
    aioclient_mock.get("http://192.0.2.10:80/state", json=state)
    config_entry = _config_entry(hass)
    api = AiraLuceApi(hass, config_entry.data)
    coordinator = AiraLuceCoordinator(hass, config_entry, api)

    assert await coordinator._async_update_data() == state


# 2026_10_08_CL: Begin optional coverage test (Quality Scale Silver: >95%).
@pytest.mark.parametrize(
    "response_kwargs",
    [
        pytest.param({"text": "not valid json"}, id="malformed-json"),
        pytest.param({"exc": aiohttp.ClientError()}, id="client-error"),
    ],
)
async def test_coordinator_wraps_http_state_errors(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    response_kwargs: dict[str, Any],
) -> None:
    """Wrap invalid responses and client errors as UpdateFailed."""
    aioclient_mock.get("http://192.0.2.10:80/state", **response_kwargs)
    config_entry = _config_entry(hass)
    api = AiraLuceApi(hass, config_entry.data)
    coordinator = AiraLuceCoordinator(hass, config_entry, api)

    with pytest.raises(UpdateFailed, match="AVITANA aira luce update failed"):
        await coordinator._async_update_data()


# 2026_10_08_CL: End optional coverage test.
@pytest.mark.parametrize(
    "error",
    [asyncio.TimeoutError, ValueError, aiohttp.ClientError],
)
async def test_coordinator_wraps_state_request_errors(
    hass: HomeAssistant, error: type[Exception]
) -> None:
    """Wrap exceptions raised while requesting device state."""
    config_entry = _config_entry(hass)
    api = AiraLuceApi(hass, config_entry.data)
    coordinator = AiraLuceCoordinator(hass, config_entry, api)

    with (
        patch.object(
            api,
            "async_get_state",
            new=AsyncMock(side_effect=error("failed")),
        ),
        pytest.raises(UpdateFailed, match="AVITANA aira luce update failed"),
    ):
        await coordinator._async_update_data()
