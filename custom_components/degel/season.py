"""Where a moment falls relative to the thaw periods: before, during, after, and the window around them."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timedelta

from .api import ThawZone

UPCOMING = "upcoming"
ACTIVE = "active"
ENDED = "ended"


def status(zone: ThawZone, now: datetime) -> str:
    if now < zone.start:
        return UPCOMING
    return ACTIVE if now < zone.ends_at else ENDED


def window(zone: ThawZone, days_before: int, days_after: int) -> tuple[datetime, datetime]:
    """From `days_before` days before the start until `days_after` days after the end."""
    return zone.start - timedelta(days=days_before), zone.ends_at + timedelta(days=days_after)


def in_season(zones: Iterable[ThawZone], now: datetime, days_before: int, days_after: int) -> bool:
    """True while `now` is in the window around any of the zones' periods."""
    for zone in zones:
        start, end = window(zone, days_before, days_after)
        if start <= now < end:
            return True
    return False


def transitions(zones: Iterable[ThawZone], days_before: int, days_after: int) -> list[datetime]:
    """Every moment a state can change, sorted."""
    moments: set[datetime] = set()
    for zone in zones:
        moments.update((zone.start, zone.ends_at, *window(zone, days_before, days_after)))
    return sorted(moments)
