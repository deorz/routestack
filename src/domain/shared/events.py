from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from domain.shared.entity_id import EntityId, new_entity_id
from domain.shared.time import utc_now


class DomainEvent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True)

    event_id: EntityId = Field(default_factory=new_entity_id)
    occurred_at: AwareDatetime = Field(default_factory=utc_now)
