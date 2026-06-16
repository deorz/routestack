from typing import Annotated

from pydantic import AwareDatetime, Field, StringConstraints

from domain.shared.entity import Entity
from domain.shared.time import utc_now

RequiredText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class AdminUser(Entity):
    login: RequiredText
    password_hash: RequiredText
    last_login_at: AwareDatetime | None = None
    disabled_at: AwareDatetime | None = None
    created_at: AwareDatetime = Field(default_factory=utc_now)
