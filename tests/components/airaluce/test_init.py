"""Tests for AVITANA aira luce config entry setup and unload."""

from unittest.mock import AsyncMock, patch

from homeassistant.components.airaluce.const import DOMAIN, PLATFORMS
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry
from tests.test_util.aiohttp import AiohttpClientMocker


async def _setup_entry(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="airaluce-unload-test",
        data={CONF_HOST: "192.0.2.10", CONF_PORT: 80},
    )
    entry.add_to_hass(hass)
    aioclient_mock.get("http://192.0.2.10:80/api/info", json={})
    aioclient_mock.get("http://192.0.2.10:80/state", json={})

    with patch.object(
        hass.config_entries,
        "async_forward_entry_setups",
        new=AsyncMock(),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
    return entry


async def test_setup_entry_loads_supported_platforms(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Set up the entry and forward all supported platforms."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="airaluce-123",
        data={CONF_HOST: "192.0.2.10", CONF_PORT: 80, "device_name": "Living room"},
    )
    entry.add_to_hass(hass)
    aioclient_mock.get(
        "http://192.0.2.10:80/api/info",
        json={
            "manufacturer": "AiraLuce",
            "model": "AL-1",
            "sw_version": "1.2.3",
            "web_url": "http://192.0.2.10/",
            "supports": {"selection": True},
        },
    )
    state = {"power": True}
    aioclient_mock.get("http://192.0.2.10:80/state", json=state)

    with patch.object(
        hass.config_entries,
        "async_forward_entry_setups",
        new=AsyncMock(),
    ) as forward_setups:
        assert await hass.config_entries.async_setup(entry.entry_id)

    assert entry.runtime_data.coordinator.data == state
    assert entry.runtime_data.api.manufacturer == "AiraLuce"
    assert entry.runtime_data.api.model == "AL-1"
    assert entry.runtime_data.api.sw_version == "1.2.3"
    assert entry.runtime_data.api.web_url == "http://192.0.2.10/"
    forward_setups.assert_awaited_once_with(entry, PLATFORMS)


async def test_setup_entry_retries_when_info_api_fails(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Schedule a retry when the info request fails."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="airaluce-123",
        data={CONF_HOST: "192.0.2.10", CONF_PORT: 80},
    )
    entry.add_to_hass(hass)
    aioclient_mock.get("http://192.0.2.10:80/api/info", status=500)

    await hass.config_entries.async_setup(entry.entry_id)

    assert entry.state is ConfigEntryState.SETUP_RETRY


async def test_unload_entry_unloads_platforms(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Unload all AVITANA aira luce platforms."""
    entry = await _setup_entry(hass, aioclient_mock)

    with patch.object(
        hass.config_entries,
        "async_unload_platforms",
        new=AsyncMock(return_value=True),
    ) as unload_platforms:
        assert await hass.config_entries.async_unload(entry.entry_id)

    unload_platforms.assert_awaited_once_with(entry, PLATFORMS)
    assert entry.state is ConfigEntryState.NOT_LOADED


# 2026_10_07_CL: Begin optional robustness test; not explicitly required by Home Assistant.
async def test_unload_entry_returns_false_when_platform_unload_fails(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Return false when platform unloading fails."""
    entry = await _setup_entry(hass, aioclient_mock)

    with patch.object(
        hass.config_entries,
        "async_unload_platforms",
        new=AsyncMock(return_value=False),
    ):
        assert not await hass.config_entries.async_unload(entry.entry_id)
