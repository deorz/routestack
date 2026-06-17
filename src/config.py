from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="ROUTESTACK_REDIS_", extra="ignore")

    URL: str = "redis://localhost:6379/0"


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="ROUTESTACK_APP_", extra="ignore")

    NAME: str = "RouteStack"


class ServerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="ROUTESTACK_SERVER_", extra="ignore")

    HOST: str = "127.0.0.1"
    PORT: int = 8000


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="ROUTESTACK_DATABASE_", extra="ignore")

    URL: str = "sqlite:///./routestack.db"


class SecuritySettings(BaseSettings):
    DEFAULT_SECRET_KEY: ClassVar[str] = "change-me-in-production"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="ROUTESTACK_SECURITY_", extra="ignore")

    SECRET_KEY: str = DEFAULT_SECRET_KEY


class APIConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="ROUTESTACK_API_", extra="ignore")

    ROOT_PREFIX: str = ""
    DOCS_ENABLED: bool = True


class AdminSessionSettings(BaseSettings):
    DEFAULT_TTL_SECONDS: ClassVar[int] = 60 * 60 * 12

    model_config = SettingsConfigDict(env_file=".env", env_prefix="ROUTESTACK_ADMIN_SESSION_", extra="ignore")

    TTL_SECONDS: int = Field(default=DEFAULT_TTL_SECONDS, gt=0)
    COOKIE_NAME: str = Field(default="routestack_admin_session", min_length=1)
    COOKIE_SECURE: bool = False


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__", extra="ignore")

    APP: AppSettings = Field(default_factory=AppSettings)
    SERVER: ServerSettings = Field(default_factory=ServerSettings)
    DATABASE: DatabaseSettings = Field(default_factory=DatabaseSettings)
    SECURITY: SecuritySettings = Field(default_factory=SecuritySettings)
    ADMIN_SESSION: AdminSessionSettings = Field(default_factory=AdminSessionSettings)

    API: APIConfig = Field(default_factory=APIConfig)

    REDIS: RedisSettings = Field(default_factory=RedisSettings)
