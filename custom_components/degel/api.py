"""Client for the thaw zones published by Transports Québec (Données Québec dataset "Zone de dégel")."""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from datetime import datetime, timedelta

import aiohttp

from .const import QUEBEC_TZ

# WFS service behind the dataset's CSV resource. Without a bbox it returns the three zones,
# without their geometry; with a point bbox, only the zone that contains it.
WFS_URL = "https://ws.mapserver.transports.gouv.qc.ca/swtq"
WFS_PARAMS = {
    "service": "wfs",
    "version": "2.0.0",
    "request": "getfeature",
    "typename": "ms:zone_degel",
    "outputformat": "csv",
}
TIMEOUT = aiohttp.ClientTimeout(total=30)

# "2026-03-16  00h01" (two spaces in the published file; any whitespace accepted).
_DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})\s+(\d{1,2})h(\d{2})")


class ThawApiError(Exception):
    """The service could not be reached or returned something unexpected."""


@dataclass(frozen=True)
class ThawZone:
    """One thaw zone and its period, as published.

    `end` is the published last minute (23:59); the period is over one minute later.
    """

    number: int
    name: str
    start: datetime
    end: datetime

    @property
    def ends_at(self) -> datetime:
        return self.end + timedelta(minutes=1)


def parse_datetime(text: str) -> datetime:
    """Québec local time from "YYYY-MM-DD  HHhMM"."""
    match = _DATE.search(text)
    if not match:
        raise ThawApiError(f"Unexpected date: {text!r}")
    year, month, day, hour, minute = (int(g) for g in match.groups())
    return datetime(year, month, day, hour, minute, tzinfo=QUEBEC_TZ)


def parse_zones(text: str) -> dict[int, ThawZone]:
    """Zones by number from the WFS CSV."""
    zones: dict[int, ThawZone] = {}
    try:
        for row in csv.DictReader(io.StringIO(text.lstrip("﻿"))):
            number = int(float(row["num_zone"]))
            zones[number] = ThawZone(
                number=number,
                name=row["nom_partie_zone"].strip(),
                start=parse_datetime(row["dat_debut_zone"]),
                end=parse_datetime(row["dat_fin_zone"]),
            )
    except (KeyError, ValueError) as err:
        raise ThawApiError(f"Unexpected CSV: {err}") from err
    return zones


class ThawClient:
    """Fetches the thaw zones; the file is a few hundred bytes."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    async def _async_get(self, extra: dict[str, str] | None = None) -> dict[int, ThawZone]:
        try:
            async with self._session.get(WFS_URL, params={**WFS_PARAMS, **(extra or {})}, timeout=TIMEOUT) as resp:
                resp.raise_for_status()
                text = await resp.text(encoding="utf-8")
        except (aiohttp.ClientError, TimeoutError) as err:
            raise ThawApiError(str(err)) from err
        return parse_zones(text)

    async def async_get_zones(self) -> dict[int, ThawZone]:
        zones = await self._async_get()
        if not zones:
            raise ThawApiError("No thaw zones returned")
        return zones

    async def async_zone_at(self, latitude: float, longitude: float) -> int | None:
        """The zone containing a point, or None outside Québec's thaw zones."""
        point = f"{latitude},{longitude},{latitude},{longitude},urn:ogc:def:crs:EPSG::4326"
        zones = await self._async_get({"bbox": point})
        return min(zones) if zones else None
