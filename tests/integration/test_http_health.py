from application.settings import AppSettings


def test_healthcheck_returns_service_status(app_client_factory) -> None:
    client = app_client_factory()

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "RouteStack"}


def test_healthcheck_uses_settings_from_container(app_client_factory) -> None:
    client = app_client_factory(AppSettings(app_name="InjectedStack"))

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "InjectedStack"}
