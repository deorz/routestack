from fastapi.testclient import TestClient

from application.settings import AppSettings
from infrastructure.container import create_container
from presentation.http.app import create_app


def test_healthcheck_returns_service_status() -> None:
    client = TestClient(create_app())

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "RouteStack"}


def test_healthcheck_uses_settings_from_container() -> None:
    container = create_container()
    container.settings.override(AppSettings(app_name="InjectedStack"))
    client = TestClient(create_app(container=container))

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "InjectedStack"}
