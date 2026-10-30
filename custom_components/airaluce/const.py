"""Constants for the AVITANA aira luce integration."""

from homeassistant.const import Platform

DOMAIN = "airaluce"

CONF_DEVICE_NAME = "device_name"
CONF_API_BASE = "api_base"
CONF_WEB_URL = "web_url"
DEFAULT_PORT = 80
SCAN_INTERVAL_SECONDS = 1

PLATFORMS: list[Platform] = [
    Platform.FAN,
    Platform.LIGHT,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]
