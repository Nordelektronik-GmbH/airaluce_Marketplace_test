"""Tests for the AVITANA aira luce fan entity."""

import pytest

from homeassistant.components.airaluce.const import DOMAIN
from homeassistant.const import CONF_HOST, CONF_PORT, STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry
from tests.test_util.aiohttp import AiohttpClientMocker


# 2026_10_21_CL: Geaendert: Fan-HA-Zustand bei Master-Aus mit gespeichertem Sollwert pruefen.
# Warum: Die Firmware stoppt den physischen Fan am Master, behaelt aber den Fan-Sollwert in /state.
# Wirkung: Der Test sichert Fan=off bei Master-Aus und den weiterhin angezeigten Sollwert ab.
# alt: Der Fan-Test rief die Entity-Property direkt auf und pruefte keinen veroeffentlichten HA-Zustand.
@pytest.mark.parametrize(
    ("master_power", "fan_value", "expected_state", "expected_percentage"),
    [
        pytest.param(0, 64, STATE_OFF, 25, id="master-off-retained-fan-speed"),
        pytest.param(1, 64, STATE_ON, 25, id="master-on-fan-running"),
        pytest.param(1, 0, STATE_OFF, 0, id="master-on-fan-stopped"),
    ],
)
async def test_fan_state_uses_master_power_and_retains_speed(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    master_power: int,
    fan_value: int,
    expected_state: str,
    expected_percentage: int,
) -> None:
    """Expose the physical fan state while retaining its configured speed."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="airaluce-fan-test",
        data={CONF_HOST: "192.0.2.10", CONF_PORT: 80},
    )
    entry.add_to_hass(hass)
    aioclient_mock.get("http://192.0.2.10:80/api/info", json={})
    aioclient_mock.get(
        "http://192.0.2.10:80/state",
        json={"on": master_power, "fan": fan_value},
    )

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("fan.airaluce_fan")
    assert state is not None
    assert state.state == expected_state
    assert state.attributes["percentage"] == expected_percentage