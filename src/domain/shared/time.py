from datetime import UTC, datetime
from typing import Protocol

from domain.shared.errors import DomainValidationError


class Clock(Protocol):
    def now(self) -> datetime:
        """Return the current timestamp."""


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


def utc_now(clock: Clock | None = None) -> datetime:
    moment = SystemClock().now() if clock is None else clock.now()
    return ensure_utc(moment, "moment")


def ensure_utc(moment: datetime, field_name: str) -> datetime:
    if not isinstance(moment, datetime):
        raise DomainValidationError(f"{field_name} must be a datetime")

    if moment.tzinfo is None or moment.utcoffset() is None:
        raise DomainValidationError(f"{field_name} must be timezone-aware")

    return moment.astimezone(UTC)


def ensure_optional_utc(moment: datetime | None, field_name: str) -> datetime | None:
    if moment is None:
        return None

    return ensure_utc(moment, field_name)
