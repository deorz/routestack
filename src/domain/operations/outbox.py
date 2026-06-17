from typing import Any

from pydantic import AwareDatetime

from domain.shared.entity import Entity
from domain.shared.types import RequiredText


class OutboxMessage(Entity):
    event_type: RequiredText
    payload: dict[str, Any]
    created_at: AwareDatetime
