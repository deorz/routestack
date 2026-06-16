from pydantic import AwareDatetime, Field

from domain.shared.entity import Entity
from domain.shared.time import utc_now
from domain.shared.types import RequiredText


class AdminUser(Entity):
    login: RequiredText
    password_hash: RequiredText
    last_login_at: AwareDatetime | None = None
    disabled_at: AwareDatetime | None = None
    created_at: AwareDatetime = Field(default_factory=utc_now)
