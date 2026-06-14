from application.settings import AppSettings
from infrastructure.container import create_container


def test_container_provides_settings_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("ROUTESTACK_APP_NAME", "RouteStack Test")
    monkeypatch.setenv("ROUTESTACK_ENVIRONMENT", "test")
    monkeypatch.setenv("ROUTESTACK_DATABASE_URL", "sqlite:///./test.db")
    monkeypatch.setenv("ROUTESTACK_SECRET_KEY", "test-secret")

    container = create_container()

    settings = container.settings()

    assert isinstance(settings, AppSettings)
    assert settings.app_name == "RouteStack Test"
    assert settings.environment == "test"
    assert settings.database_url == "sqlite:///./test.db"
    assert settings.secret_key == "test-secret"


def test_container_allows_provider_overrides() -> None:
    container = create_container()
    override = AppSettings(app_name="OverrideStack")

    with container.settings.override(override):
        settings = container.settings()

    assert hasattr(container, "settings")
    assert settings.app_name == "OverrideStack"
