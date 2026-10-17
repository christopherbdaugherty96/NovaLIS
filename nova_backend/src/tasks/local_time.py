from __future__ import annotations

from datetime import date, datetime, time, timezone, tzinfo


def as_local(value: datetime, local_zone: tzinfo | None = None) -> datetime:
    """Convert an aware datetime using injected or operating-system local rules."""
    if value.tzinfo is None:
        raise ValueError("An aware datetime is required.")
    return value.astimezone(local_zone) if local_zone is not None else value.astimezone()


def resolve_local_wall_time(
    local_date: date,
    local_time: time,
    *,
    local_zone: tzinfo | None = None,
) -> datetime:
    """Resolve a wall time, rejecting gaps and choosing the first fold occurrence."""
    naive = datetime.combine(local_date, local_time).replace(second=0, microsecond=0)
    candidates: list[datetime] = []
    seen_instants: set[datetime] = set()

    for fold in (0, 1):
        if local_zone is None:
            candidate = naive.replace(fold=fold).astimezone()
            round_trip = candidate.astimezone(timezone.utc).astimezone()
        else:
            candidate = naive.replace(tzinfo=local_zone, fold=fold)
            round_trip = candidate.astimezone(timezone.utc).astimezone(local_zone)
        if round_trip.replace(tzinfo=None) != naive:
            continue
        instant = candidate.astimezone(timezone.utc)
        if instant in seen_instants:
            continue
        seen_instants.add(instant)
        candidates.append(candidate)

    if not candidates:
        rendered = naive.strftime("%b %d at %I:%M %p").replace(" 0", " ")
        raise ValueError(
            f"That local time ({rendered}) does not exist because the clocks move forward. "
            "Choose a time after the clock change."
        )

    return min(candidates, key=lambda item: item.astimezone(timezone.utc))
