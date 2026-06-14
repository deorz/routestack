from dataclasses import dataclass, field
from datetime import datetime

from domain.shared.entity_id import EntityId, new_entity_id
from domain.shared.time import ensure_utc, utc_now
from domain.shared.validation import ensure_type


@dataclass(slots=True, kw_only=True)
class DomainEvent:
    event_id: EntityId = field(default_factory=new_entity_id)
    occurred_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.event_id = ensure_type(self.event_id, EntityId, "event_id")
        self.occurred_at = ensure_utc(self.occurred_at, "occurred_at")
