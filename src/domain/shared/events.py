from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from domain.shared.entity_id import EntityId
from domain.shared.time import ensure_utc, utc_now


@dataclass(frozen=True, slots=True, kw_only=True)
class DomainEvent:
    event_id: EntityId = field(default_factory=EntityId.new)
    occurred_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        object.__setattr__(self, "occurred_at", ensure_utc(self.occurred_at, "occurred_at"))
