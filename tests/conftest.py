"""Fixtures for the Dégel tests."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

FIXTURES = Path(__file__).parent / "fixtures"

# Recorded 2026-10-22: zone 1 from 2026-03-16 00h01 to 2026-05-15 23h59, zone 2 from 04-13 to 05-22,
# zone 3 from 04-20 to 05-29.
DURING_ZONE_1 = "2026-04-01T16:00:00+00:00"  # 12:00 in Québec: zone 1 in effect, 2 and 3 upcoming
SAGUENAY = (48.43, -71.07)  # zone 2


def load_text(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Load custom_components/ in every test."""
    yield


@pytest.fixture
async def quebec_home(hass):
    """Home Assistant located in Saguenay."""
    await hass.config.async_set_time_zone("America/Toronto")
    hass.config.latitude, hass.config.longitude = SAGUENAY
    hass.config.country = "CA"
    return hass


@pytest.fixture
def mtq_api(aioclient_mock: AiohttpClientMocker) -> AiohttpClientMocker:
    """Serve recorded WFS responses: the three zones, or Saguenay's zone for a point lookup."""
    aioclient_mock.get(re.compile(r"swtq\?.*bbox="), text=load_text("zone_saguenay.csv"))
    aioclient_mock.get(re.compile(r"swtq\?"), text=load_text("zone_degel.csv"))
    return aioclient_mock
