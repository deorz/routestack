from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from domain.shared.entity_id import EntityId, ensure_entity_id, new_entity_id
from domain.shared.time import ensure_utc, utc_now


class DomainEvent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=False)

    event_id: EntityId = Field(default_factory=new_entity_id)
    occurred_at: datetime = Field(default_factory=utc_now)

    @field_validator("event_id", mode="before")
    @classmethod
    def validate_event_id(cls, value: object) -> EntityId:
        return ensure_entity_id(value, "event_id")

    @field_validator("occurred_at", mode="before")
    @classmethod
    def validate_occurred_at(cls, value: datetime) -> datetime:
        return ensure_utc(value, "occurred_at")
