from typing import ClassVar

from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseModel):
    name: str = "RouteStack"
    environment: str = "local"


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class DatabaseConfig(BaseModel):
    url: str = "sqlite:///./routestack.db"


class SecurityConfig(BaseModel):
    DEFAULT_SECRET_KEY: ClassVar[str] = "change-me-in-production"
    MIN_SECRET_KEY_LENGTH: ClassVar[int] = 32
    NON_STRONG_SECRET_ENVIRONMENTS: ClassVar[frozenset[str]] = frozenset({"local", "test"})

    secret_key: str = DEFAULT_SECRET_KEY

    def validate_for_environment(self, environment: str) -> None:
        if environment in self.NON_STRONG_SECRET_ENVIRONMENTS:
            return

        if self.secret_key == self.DEFAULT_SECRET_KEY or len(self.secret_key) < self.MIN_SECRET_KEY_LENGTH:
            raise ValueError("secret_key must be a strong explicit value in non-local/test environments")


class AdminSessionConfig(BaseModel):
    DEFAULT_TTL_SECONDS: ClassVar[int] = 60 * 60 * 12

    ttl_seconds: int = Field(default=DEFAULT_TTL_SECONDS, gt=0)
    cookie_name: str = Field(
        default="routestack_admin_session",
        min_length=1,
        pattern=r"^[A-Za-z0-9!#$%&'*+.^_`|~-]+$",
    )


class AppSettings(BaseSettings):
    DEFAULT_SECRET_KEY: ClassVar[str] = SecurityConfig.DEFAULT_SECRET_KEY
    DEFAULT_ADMIN_SESSION_TTL_SECONDS: ClassVar[int] = AdminSessionConfig.DEFAULT_TTL_SECONDS
    MIN_SECRET_KEY_LENGTH: ClassVar[int] = SecurityConfig.MIN_SECRET_KEY_LENGTH
    NON_STRONG_SECRET_ENVIRONMENTS: ClassVar[frozenset[str]] = SecurityConfig.NON_STRONG_SECRET_ENVIRONMENTS

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
        self.security.validate_for_environment(self.app.environment)

        return self

    @property
    def app(self) -> AppConfig:
        return AppConfig(name=self.app_name, environment=self.environment)

    @property
    def server(self) -> ServerConfig:
        return ServerConfig(host=self.server_host, port=self.server_port)

    @property
    def database(self) -> DatabaseConfig:
        return DatabaseConfig(url=self.database_url)

    @property
    def security(self) -> SecurityConfig:
        return SecurityConfig(secret_key=self.secret_key)

    @property
    def admin_session(self) -> AdminSessionConfig:
        return AdminSessionConfig(
            ttl_seconds=self.admin_session_ttl_seconds,
            cookie_name=self.admin_session_cookie_name,
        )


Settings = AppSettings
