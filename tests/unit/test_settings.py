from application.settings import AppSettings


def test_settings_have_secure_local_defaults(monkeypatch) -> None:
    monkeypatch.delenv("ROUTESTACK_APP_NAME", raising=False)
    monkeypatch.delenv("ROUTESTACK_ENVIRONMENT", raising=False)
    monkeypatch.delenv("ROUTESTACK_DATABASE_URL", raising=False)
    monkeypatch.delenv("ROUTESTACK_SECRET_KEY", raising=False)

    settings = AppSettings()

    assert settings.app_name == "RouteStack"
    assert settings.environment == "local"
    assert settings.database_url == "sqlite:///./routestack.db"
    assert settings.secret_key == "change-me-in-production"
