from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_SECRET_KEY = "change-me-in-production"
DEFAULT_ADMIN_SESSION_TTL_SECONDS = 60 * 60 * 12
MIN_SECRET_KEY_LENGTH = 32
NON_STRONG_SECRET_ENVIRONMENTS = {"local", "test"}


class AppSettings(BaseSettings):
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
    server_host: str = "0.0.0.0"
    server_port: int = 8000

    @model_validator(mode="after")
    def validate_secret_key_strength(self) -> "AppSettings":
        if self.environment not in NON_STRONG_SECRET_ENVIRONMENTS and self._secret_key_is_weak():
            raise ValueError("secret_key must be a strong explicit value in non-local/test environments")

        return self

    def _secret_key_is_weak(self) -> bool:
        return self.secret_key == DEFAULT_SECRET_KEY or len(self.secret_key) < MIN_SECRET_KEY_LENGTH
