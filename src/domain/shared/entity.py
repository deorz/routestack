from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, field_validator

from domain.shared.entity_id import EntityId, ensure_entity_id, new_entity_id
from domain.shared.events import DomainEvent
from domain.shared.validation import ensure_type


class Entity(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=False)

    id: EntityId = Field(default_factory=new_entity_id)
    _domain_events: list[DomainEvent] = PrivateAttr(default_factory=list)

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, value: object) -> EntityId:
        return ensure_entity_id(value, "id")

    def record_domain_event(self, event: DomainEvent) -> None:
        self._domain_events.append(ensure_type(event, DomainEvent, "event"))

    def pull_domain_events(self) -> tuple[DomainEvent, ...]:
        events = tuple(self._domain_events)
        self._domain_events.clear()
        return events
