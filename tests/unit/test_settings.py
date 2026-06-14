from application.settings import AppSettings


def test_settings_have_secure_local_defaults(monkeypatch) -> None:
    monkeypatch.delenv("ROUTESTACK_APP_NAME", raising=False)
    monkeypatch.delenv("ROUTESTACK_ENVIRONMENT", raising=False)
    monkeypatch.delenv("ROUTESTACK_DATABASE_URL", raising=False)
    monkeypatch.delenv("ROUTESTACK_SECRET_KEY", raising=False)
    monkeypatch.delenv("ROUTESTACK_SERVER_HOST", raising=False)
    monkeypatch.delenv("ROUTESTACK_SERVER_PORT", raising=False)

    settings = AppSettings()

    assert settings.app_name == "RouteStack"
    assert settings.environment == "local"
    assert settings.database_url == "sqlite:///./routestack.db"
    assert settings.secret_key == "change-me-in-production"
    assert settings.server_host == "0.0.0.0"
    assert settings.server_port == 8000
