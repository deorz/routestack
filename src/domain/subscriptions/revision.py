from pydantic import AwareDatetime, PositiveInt

from domain.shared.entity import Entity
from domain.shared.entity_id import EntityId
from domain.shared.types import RequiredText


class SubscriptionRevision(Entity):
    subscription_id: EntityId
    revision: PositiveInt
    safe_change_summary: RequiredText
    created_at: AwareDatetime
    created_by: RequiredText | None = None
