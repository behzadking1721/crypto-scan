"""Clock abstraction."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol, runtime_checkable


@runtime_checkable
class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class FixedClock:
    def __init__(self, value: datetime) -> None:
        if value.tzinfo is None:
            raise ValueError("value must be timezone-aware")
        self._value = value.astimezone(timezone.utc)

    def now(self) -> datetime:
        return self._value
