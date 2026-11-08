"""Myanmar Time helpers. MMT is UTC+6:30, no DST."""

from datetime import date, datetime, timedelta, timezone

MMT = timezone(timedelta(hours=6, minutes=30))


def day_bounds(day: date) -> tuple[int, int]:
    """UTC epoch bounds [start, end) of a Myanmar-calendar day."""
    start = datetime(day.year, day.month, day.day, tzinfo=MMT)
    end = start + timedelta(days=1)
    return int(start.timestamp()), int(end.timestamp())


def today_mmt() -> date:
    return datetime.now(MMT).date()


def now_mmt_iso() -> str:
    return datetime.now(MMT).isoformat()
