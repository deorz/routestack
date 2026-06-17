from enum import StrEnum
from typing import Any

from pydantic import AwareDatetime, Field

from domain.shared.entity import Entity
from domain.shared.entity_id import EntityId
from domain.shared.types import RequiredText


class AuditAction(StrEnum):
    ADMIN_BOOTSTRAP = "admin.bootstrap"
    ADMIN_LOGIN = "admin.login"


class AuditRecord(Entity):
    actor_id: EntityId | None = None
    action: AuditAction
    entity_type: RequiredText
    entity_id: EntityId
    metadata: dict[str, Any] = Field(default_factory=dict)
    source_ip: str | None = None
    created_at: AwareDatetime
