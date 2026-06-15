from application.settings import AppSettings
from domain.clients.client import Client
from infrastructure.container import create_container
from infrastructure.db import Base


def test_container_provides_settings_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("ROUTESTACK_APP_NAME", "RouteStack Test")
    monkeypatch.setenv("ROUTESTACK_ENVIRONMENT", "test")
    monkeypatch.setenv("ROUTESTACK_DATABASE_URL", "sqlite:///./test.db")
    monkeypatch.setenv("ROUTESTACK_SECRET_KEY", "test-secret")

    container = create_container()

    settings = container.settings()

    assert isinstance(settings, AppSettings)
    assert settings.app.name == "RouteStack Test"
    assert settings.app.environment == "test"
    assert settings.database.url == "sqlite:///./test.db"
    assert settings.security.secret_key == "test-secret"


def test_container_allows_provider_overrides() -> None:
    container = create_container()
    override = AppSettings(app_name="OverrideStack")

    with container.settings.override(override):
        settings = container.settings()

    assert hasattr(container, "settings")
    assert settings.app.name == "OverrideStack"


def test_container_wires_database_unit_of_work(tmp_path) -> None:
    container = create_container()
    settings = AppSettings(database_url=f"sqlite:///{tmp_path / 'container.db'}")

    with container.settings.override(settings):
        engine = container.db_engine()
        Base.metadata.create_all(engine)

        client = Client(display_name="Container Client")

        with container.unit_of_work() as unit_of_work:
            unit_of_work.clients.add(client)
            unit_of_work.commit()

        with container.unit_of_work() as unit_of_work:
            loaded = unit_of_work.clients.get(client.id)

    assert loaded is not None
    assert loaded.display_name == "Container Client"
