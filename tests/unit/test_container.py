from config import AppSettings, Config, DatabaseSettings, SecuritySettings
from containers import create_container
from domain.clients.client import Client
from infra.db import Base


def test_container_provides_settings_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("ROUTESTACK_APP_NAME", "RouteStack Test")
    monkeypatch.setenv("ROUTESTACK_DATABASE_URL", "sqlite:///./test.db")
    monkeypatch.setenv("ROUTESTACK_SECURITY_SECRET_KEY", "test-secret")

    container = create_container()

    settings = container.settings()

    assert isinstance(settings, Config)
    assert settings.APP.NAME == "RouteStack Test"
    assert settings.DATABASE.URL == "sqlite:///./test.db"
    assert settings.SECURITY.SECRET_KEY == "test-secret"


def test_container_allows_provider_overrides() -> None:
    container = create_container()
    override = Config(APP=AppSettings(NAME="OverrideStack"))

    with container.settings.override(override):
        settings = container.settings()

    assert hasattr(container, "settings")
    assert settings.APP.NAME == "OverrideStack"


def test_container_wires_database_unit_of_work(tmp_path) -> None:
    container = create_container()
    settings = Config(
        DATABASE=DatabaseSettings(URL=f"sqlite:///{tmp_path / 'container.db'}"),
        SECURITY=SecuritySettings(SECRET_KEY="test-secret"),
    )

    with container.settings.override(settings):
        engine = container.db_engine()
        Base.metadata.create_all(engine)

        client = Client(display_name="Container Client")

        with container.unit_of_work() as unit_of_work:
            unit_of_work.clients.add(client)

        with container.unit_of_work() as unit_of_work:
            loaded = unit_of_work.clients.get(client.id)

    assert loaded is not None
    assert loaded.display_name == "Container Client"
