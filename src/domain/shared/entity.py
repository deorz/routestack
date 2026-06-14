from dataclasses import dataclass, field
from typing import TypeVar

from domain.shared.entity_id import EntityId, new_entity_id
from domain.shared.events import DomainEvent
from domain.shared.validation import ensure_type

T = TypeVar("T")


@dataclass(slots=True, kw_only=True, eq=False)
class Entity:
    id: EntityId = field(default_factory=new_entity_id)
    _domain_events: list[DomainEvent] = field(
        default_factory=list,
        init=False,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        self._ensure_type(self.id, EntityId, "id")

    def record_domain_event(self, event: DomainEvent) -> None:
        self._domain_events.append(self._ensure_type(event, DomainEvent, "event"))

    def pull_domain_events(self) -> tuple[DomainEvent, ...]:
        events = tuple(self._domain_events)
        self._domain_events.clear()
        return events

    @staticmethod
    def _ensure_type(value: object, expected_type: type[T], field_name: str) -> T:
        return ensure_type(value, expected_type, field_name)
