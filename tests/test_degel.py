"""Tests for the Dégel integration: parsing, season logic, flows and entities."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.degel.api import ThawApiError, parse_datetime, parse_zones
from custom_components.degel.const import DOMAIN, QUEBEC_TZ
from custom_components.degel.season import ACTIVE, ENDED, UPCOMING, in_season, status, transitions

from .conftest import DURING_ZONE_1, load_text

INTEGRATION = Path(__file__).parent.parent / "custom_components" / DOMAIN


def _local(*args: int) -> datetime:
    return datetime(*args, tzinfo=QUEBEC_TZ)


# ---------- parsing and season logic ----------


def test_parse_recorded_csv() -> None:
    zones = parse_zones(load_text("zone_degel.csv"))
    assert sorted(zones) == [1, 2, 3]
    assert zones[1].name == "Partie sud du Québec"
    assert zones[1].start == _local(2026, 3, 16, 0, 1)
    assert zones[1].end == _local(2026, 5, 15, 23, 59)
    assert zones[1].ends_at == _local(2026, 5, 16, 0, 0)
    assert zones[3].start == _local(2026, 4, 20, 0, 1)


def test_parse_accepts_one_space_and_rejects_garbage() -> None:
    assert parse_datetime("2027-03-01 0h01") == _local(2027, 3, 1, 0, 1)
    with pytest.raises(ThawApiError):
        parse_datetime("le 1er mars")
    with pytest.raises(ThawApiError):
        parse_zones("zone,autre\nZone 1,x\n")
    assert parse_zones(load_text("zone_empty.csv")) == {}


def test_status_and_window_edges() -> None:
    zone = parse_zones(load_text("zone_degel.csv"))[1]
    assert status(zone, _local(2026, 3, 16, 0, 0)) == UPCOMING
    assert status(zone, _local(2026, 3, 16, 0, 1)) == ACTIVE
    assert status(zone, _local(2026, 5, 15, 23, 59, 59)) == ACTIVE
    assert status(zone, _local(2026, 5, 16, 0, 0)) == ENDED

    assert not in_season([zone], _local(2026, 3, 1, 0, 0), 14, 7)
    assert in_season([zone], _local(2026, 3, 2, 0, 1), 14, 7)
    assert in_season([zone], _local(2026, 5, 22, 23, 59), 14, 7)
    assert not in_season([zone], _local(2026, 5, 23, 0, 0), 14, 7)
    assert transitions([zone], 0, 0) == [zone.start, zone.ends_at]


def test_translations_match_strings() -> None:
    """en.json is a copy of strings.json, and fr.json has exactly the same keys."""

    def keys(node, path=""):
        if isinstance(node, dict):
            return {k for key, value in node.items() for k in keys(value, f"{path}.{key}")}
        return {path}

    strings = json.loads((INTEGRATION / "strings.json").read_text(encoding="utf-8"))
    for language in ("en", "fr"):
        translation = json.loads((INTEGRATION / "translations" / f"{language}.json").read_text(encoding="utf-8"))
        assert keys(translation) == keys(strings), language
    assert json.loads((INTEGRATION / "translations" / "en.json").read_text(encoding="utf-8")) == strings


# ---------- config and options flows ----------


async def _setup(hass: HomeAssistant, zones: list[str]) -> config_entries.ConfigEntry:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"zones": zones, "days_before": 14, "days_after": 7}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    return result["result"]


@pytest.mark.freeze_time(DURING_ZONE_1)
async def test_user_flow_preselects_home_zone(quebec_home, mtq_api) -> None:
    hass = quebec_home
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] is FlowResultType.FORM
    assert result["data_schema"]({})["zones"] == ["2"]  # Saguenay

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"zones": ["2", "1"], "days_before": 10, "days_after": 3}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Dégel"
    assert result["result"].options == {"zones": [1, 2], "days_before": 10, "days_after": 3}


async def test_user_flow_outside_quebec_defaults_to_zone_1(hass, aioclient_mock: AiohttpClientMocker) -> None:
    aioclient_mock.get("https://ws.mapserver.transports.gouv.qc.ca/swtq", text=load_text("zone_empty.csv"))
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["data_schema"]({})["zones"] == ["1"]


async def test_user_flow_errors(quebec_home, aioclient_mock: AiohttpClientMocker) -> None:
    hass = quebec_home
    aioclient_mock.get("https://ws.mapserver.transports.gouv.qc.ca/swtq", status=503)
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["data_schema"]({})["zones"] == ["1"]  # lookup failed: the default

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"zones": [], "days_before": 14, "days_after": 7}
    )
    assert result["errors"] == {"zones": "no_zone"}

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"zones": ["1"], "days_before": 14, "days_after": 7}
    )
    assert result["errors"] == {"base": "cannot_connect"}


async def test_single_instance(quebec_home, mtq_api) -> None:
    hass = quebec_home
    MockConfigEntry(domain=DOMAIN, options={"zones": [1]}).add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "single_instance_allowed"


# ---------- entities ----------


@pytest.mark.freeze_time(DURING_ZONE_1)
async def test_entities_during_zone_1(quebec_home, mtq_api) -> None:
    hass = quebec_home
    await _setup(hass, ["1", "2"])

    season = hass.states.get("binary_sensor.degel_thaw_season")
    assert season.state == "on"
    assert season.attributes["active_zones"] == [1]
    assert [z["status"] for z in season.attributes["thaw_zones"]] == ["active", "upcoming"]
    assert season.attributes["thaw_zones"][0]["start"] == "2026-03-16T00:01:00-04:00"
    assert season.attributes["season_start"] == "2026-03-02T00:01:00-05:00"
    assert season.attributes["season_end"] == "2026-05-30T00:00:00-04:00"

    assert hass.states.get("binary_sensor.degel_zone_1_thaw_period").state == "on"
    zone_2 = hass.states.get("binary_sensor.degel_zone_2_thaw_period")
    assert zone_2.state == "off"
    assert zone_2.attributes["name"] == "Partie médiane du Québec"
    assert hass.states.get("sensor.degel_zone_2_thaw_start").state == "2026-04-13T04:01:00+00:00"
    assert hass.states.get("sensor.degel_zone_2_thaw_end").state == "2026-05-23T03:59:00+00:00"
    assert hass.states.get("binary_sensor.degel_zone_3_thaw_period") is None


@pytest.mark.freeze_time(DURING_ZONE_1)
async def test_states_change_at_the_published_times(quebec_home, mtq_api, freezer: FrozenDateTimeFactory) -> None:
    """No poll needed: the entities update when a period starts or ends."""
    hass = quebec_home
    await _setup(hass, ["2"])
    assert hass.states.get("binary_sensor.degel_thaw_season").state == "on"  # within 14 days of 04-13
    assert hass.states.get("binary_sensor.degel_zone_2_thaw_period").state == "off"

    for moment, period, season in (
        (_local(2026, 4, 13, 0, 1), "on", "on"),
        (_local(2026, 5, 23, 0, 0), "off", "on"),
        (_local(2026, 5, 30, 0, 0), "off", "off"),
    ):
        freezer.move_to(moment)
        async_fire_time_changed(hass, moment)
        await hass.async_block_till_done()
        assert hass.states.get("binary_sensor.degel_zone_2_thaw_period").state == period, moment
        assert hass.states.get("binary_sensor.degel_thaw_season").state == season, moment


@pytest.mark.freeze_time(DURING_ZONE_1)
async def test_options_change_zones(quebec_home, mtq_api) -> None:
    hass = quebec_home
    entry = await _setup(hass, ["1", "2"])

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["data_schema"]({})["zones"] == ["1", "2"]
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"zones": [], "days_before": 14, "days_after": 7}
    )
    assert result["errors"] == {"zones": "no_zone"}
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"zones": ["3"], "days_before": 0, "days_after": 0}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    assert registry.async_get("binary_sensor.degel_zone_1_thaw_period") is None
    assert registry.async_get("sensor.degel_zone_2_thaw_end") is None
    assert hass.states.get("binary_sensor.degel_zone_3_thaw_period").state == "off"
    assert hass.states.get("binary_sensor.degel_thaw_season").state == "off"  # zone 3 starts 04-20


@pytest.mark.freeze_time(DURING_ZONE_1)
async def test_service_down_keeps_last_dates(quebec_home, mtq_api, freezer: FrozenDateTimeFactory) -> None:
    hass = quebec_home
    await _setup(hass, ["1"])
    mtq_api.clear_requests()
    mtq_api.get("https://ws.mapserver.transports.gouv.qc.ca/swtq", status=503)

    freezer.tick(timedelta(hours=7))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert len(mtq_api.mock_calls) == 1
    assert hass.states.get("binary_sensor.degel_thaw_season").state == "on"
    assert hass.states.get("sensor.degel_zone_1_thaw_end").state == "2026-05-16T03:59:00+00:00"


@pytest.mark.freeze_time(DURING_ZONE_1)
async def test_french_entity_ids(quebec_home, mtq_api) -> None:
    """The IDs the README gives for a Home Assistant set to French."""
    hass = quebec_home
    hass.config.language = "fr"
    await _setup(hass, ["1"])

    season = hass.states.get("binary_sensor.degel_saison_de_degel")
    assert season.attributes["friendly_name"] == "Dégel Saison de dégel"
    assert hass.states.get("binary_sensor.degel_periode_de_degel_zone_1").state == "on"
    assert hass.states.get("sensor.degel_debut_du_degel_zone_1") is not None
    assert hass.states.get("sensor.degel_fin_du_degel_zone_1") is not None
