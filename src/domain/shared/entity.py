from dataclasses import dataclass, field

from domain.shared.entity_id import EntityId, ensure_entity_id, new_entity_id
from domain.shared.events import DomainEvent
from domain.shared.validation import ensure_type


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
        self.id = ensure_entity_id(self.id, "id")

    def record_domain_event(self, event: DomainEvent) -> None:
        self._domain_events.append(ensure_type(event, DomainEvent, "event"))

    def pull_domain_events(self) -> tuple[DomainEvent, ...]:
        events = tuple(self._domain_events)
        self._domain_events.clear()
        return events
