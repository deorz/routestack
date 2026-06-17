from fastapi.testclient import TestClient


def test_admin_login_flow_sets_session_cookie_and_protects_admin_route(seeded_app_client: TestClient) -> None:
    client = seeded_app_client
    container = client.app.state.container
    settings = container.settings()

    login_page = client.get("/admin/login")
    assert login_page.status_code == 200
    assert "<form" in login_page.text

    response = client.post(
        "/admin/login",
        data={"login": "root", "password": "secret-123"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/admin"
    assert settings.ADMIN_SESSION.COOKIE_NAME in response.headers.get("set-cookie", "")
    assert f"max-age={settings.ADMIN_SESSION.TTL_SECONDS}" in response.headers.get("set-cookie", "").lower()

    protected = client.get("/admin")
    assert protected.status_code == 200
    assert protected.json() == {"status": "ok", "login": "root"}

    logout = client.post("/admin/logout", follow_redirects=False)
    assert logout.status_code == 303
    assert logout.headers["location"] == "/admin/login"
    assert settings.ADMIN_SESSION.COOKIE_NAME in logout.headers.get("set-cookie", "")
    assert "Max-Age=0" in logout.headers.get("set-cookie", "")

    after_logout = client.get("/admin")
    assert after_logout.status_code == 401


def test_admin_login_rejects_invalid_credentials_without_disclosing_reason(seeded_app_client: TestClient) -> None:
    client = seeded_app_client

    wrong_password = client.post(
        "/admin/login",
        data={"login": "root", "password": "wrong"},
    )
    wrong_login = client.post(
        "/admin/login",
        data={"login": "missing", "password": "secret-123"},
    )

    assert wrong_password.status_code == 401
    assert wrong_login.status_code == 401
    assert wrong_password.text == wrong_login.text
