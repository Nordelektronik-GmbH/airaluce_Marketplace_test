# AVITANA aira luce Home Assistant Custom Integration (Prototype)

**Requirements:** Home Assistant 2026.9.0 or newer.

This folder contains a minimal custom integration with:
- Zeroconf discovery via `_airaluce._tcp.local.`
- Config flow (one-click setup from discovery)
- Native entities for power, light brightness and color temperature, fan speed, diagnostics and zone selection

## Install in Home Assistant

1. Copy `custom_components/airaluce` into your Home Assistant config folder under `custom_components/`.
2. Restart Home Assistant.
3. Go to Settings -> Devices & Services -> Add Integration.
4. Select `AVITANA aira luce` (or accept discovered device notification).

## Firmware requirements

- Device must expose `GET /api/info`
- Device must expose `GET /state`
- Device must support command endpoints:
  - `/button1`, `/button2`
  - `/slider?...`
  - `/setSelection?selection=...`
- Device should advertise mDNS service `_airaluce._tcp` on port 80.
