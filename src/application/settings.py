from typing import ClassVar

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    DEFAULT_SECRET_KEY: ClassVar[str] = "change-me-in-production"
    DEFAULT_ADMIN_SESSION_TTL_SECONDS: ClassVar[int] = 60 * 60 * 12
    MIN_SECRET_KEY_LENGTH: ClassVar[int] = 32
    NON_STRONG_SECRET_ENVIRONMENTS: ClassVar[frozenset[str]] = frozenset({"local", "test"})

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ROUTESTACK_",
        extra="ignore",
    )

    app_name: str = "RouteStack"
    environment: str = "local"
    database_url: str = "sqlite:///./routestack.db"
    secret_key: str = DEFAULT_SECRET_KEY
    admin_session_ttl_seconds: int = Field(default=DEFAULT_ADMIN_SESSION_TTL_SECONDS, gt=0)
    admin_session_cookie_name: str = Field(
        default="routestack_admin_session",
        min_length=1,
        pattern=r"^[A-Za-z0-9!#$%&'*+.^_`|~-]+$",
    )
    server_host: str = "0.0.0.0"
    server_port: int = 8000

    @model_validator(mode="after")
    def validate_secret_key_strength(self) -> "AppSettings":
        if self.environment not in self.NON_STRONG_SECRET_ENVIRONMENTS and (
            self.secret_key == self.DEFAULT_SECRET_KEY or len(self.secret_key) < self.MIN_SECRET_KEY_LENGTH
        ):
            raise ValueError("secret_key must be a strong explicit value in non-local/test environments")

        return self
