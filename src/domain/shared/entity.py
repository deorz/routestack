from __future__ import annotations

from dataclasses import dataclass, field

from domain.shared.entity_id import EntityId
from domain.shared.errors import DomainValidationError
from domain.shared.events import DomainEvent


@dataclass(slots=True, kw_only=True, eq=False)
class Entity:
    id: EntityId = field(default_factory=EntityId.new)
    _domain_events: list[DomainEvent] = field(
        default_factory=list,
        init=False,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        if not isinstance(self.id, EntityId):
            raise DomainValidationError("id must be an EntityId")

    def record_domain_event(self, event: DomainEvent) -> None:
        if not isinstance(event, DomainEvent):
            raise DomainValidationError("event must be a DomainEvent")

        self._domain_events.append(event)

    def pull_domain_events(self) -> tuple[DomainEvent, ...]:
        events = tuple(self._domain_events)
        self._domain_events.clear()
        return events
