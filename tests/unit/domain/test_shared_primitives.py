from dataclasses import dataclass
from datetime import UTC, datetime, timedelta, timezone

from domain.shared.entity import Entity
from domain.shared.events import DomainEvent
from domain.shared.time import utc_now


@dataclass(slots=True)
class DemoEvent(DomainEvent):
    message: str


def test_domain_event_defaults_are_timezone_aware_utc() -> None:
    event = DemoEvent(message="created")

    assert event.occurred_at.tzinfo is not None
    assert event.occurred_at.utcoffset() == timedelta(0)
    assert event.occurred_at.astimezone(UTC) == event.occurred_at


def test_domain_event_normalizes_aware_non_utc_datetime_to_utc() -> None:
    occurred_at = datetime(2026, 6, 14, 12, 30, tzinfo=timezone(timedelta(hours=3)))

    event = DemoEvent(message="created", occurred_at=occurred_at)

    assert event.occurred_at.tzinfo == UTC
    assert event.occurred_at == occurred_at.astimezone(UTC)


def test_entity_pull_domain_events_clears_queue() -> None:
    entity = Entity()
    event = DemoEvent(message="created")

    entity.record_domain_event(event)

    assert entity.pull_domain_events() == (event,)
    assert entity.pull_domain_events() == ()


def test_utc_now_is_timezone_aware_utc() -> None:
    now = utc_now()

    assert now.tzinfo is not None
    assert now.utcoffset() == timedelta(0)
