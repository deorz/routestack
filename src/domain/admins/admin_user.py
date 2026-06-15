from datetime import datetime

from pydantic import Field, field_validator

from domain.shared.entity import Entity
from domain.shared.time import ensure_optional_utc, ensure_utc, utc_now
from domain.shared.validation import normalize_required_text


class AdminUser(Entity):
    login: str
    password_hash: str
    last_login_at: datetime | None = None
    disabled_at: datetime | None = None
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("login", mode="before")
    @classmethod
    def validate_login(cls, value: str) -> str:
        return normalize_required_text(value, "login")

    @field_validator("password_hash", mode="before")
    @classmethod
    def validate_password_hash(cls, value: str) -> str:
        return normalize_required_text(value, "password_hash")

    @field_validator("created_at", mode="before")
    @classmethod
    def validate_created_at(cls, value: datetime) -> datetime:
        return ensure_utc(value, "created_at")

    @field_validator("last_login_at", "disabled_at", mode="before")
    @classmethod
    def validate_optional_timestamp(cls, value: datetime | None, info) -> datetime | None:
        return ensure_optional_utc(value, info.field_name)
