from dataclasses import dataclass, field
from datetime import datetime

from domain.shared.entity import Entity
from domain.shared.time import ensure_optional_utc, ensure_utc, utc_now
from domain.shared.validation import normalize_required_text


@dataclass(slots=True, kw_only=True, eq=False)
class AdminUser(Entity):
    login: str
    password_hash: str
    last_login_at: datetime | None = None
    disabled_at: datetime | None = None
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        Entity.__post_init__(self)
        self.login = normalize_required_text(self.login, "login")
        self.password_hash = normalize_required_text(self.password_hash, "password_hash")
        self.created_at = ensure_utc(self.created_at, "created_at")
        self.last_login_at = ensure_optional_utc(self.last_login_at, "last_login_at")
        self.disabled_at = ensure_optional_utc(self.disabled_at, "disabled_at")
