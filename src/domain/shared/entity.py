from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from domain.shared.entity_id import EntityId, new_entity_id
from domain.shared.events import DomainEvent
from domain.shared.validation import ensure_type


class Entity(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True)

    id: EntityId = Field(default_factory=new_entity_id)
    _domain_events: list[DomainEvent] = PrivateAttr(default_factory=list)

    def record_domain_event(self, event: DomainEvent) -> None:
        self._domain_events.append(ensure_type(event, DomainEvent, "event"))

    def pull_domain_events(self) -> tuple[DomainEvent, ...]:
        events = tuple(self._domain_events)
        self._domain_events.clear()
        return events
