from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ROUTESTACK_",
        extra="ignore",
    )

    app_name: str = "RouteStack"
    environment: str = "local"
    database_url: str = "sqlite:///./routestack.db"
    secret_key: str = "change-me-in-production"
    server_host: str = "0.0.0.0"
    server_port: int = 8000
