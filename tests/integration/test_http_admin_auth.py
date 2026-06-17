from config import AdminSessionSettings, AppSettings, Config, DatabaseSettings, SecuritySettings
from infra.db import Base


def _database_url(tmp_path, name: str) -> str:
    return f"sqlite:///{tmp_path / name}"


def test_admin_login_flow_sets_session_cookie_and_protects_admin_route(app_client_factory, tmp_path) -> None:
    settings = Config(
        APP=AppSettings(NAME="InjectedStack"),
        DATABASE=DatabaseSettings(URL=_database_url(tmp_path, "admin-auth-flow.db")),
        SECURITY=SecuritySettings(SECRET_KEY="integration-secret"),
        ADMIN_SESSION=AdminSessionSettings(TTL_SECONDS=AdminSessionSettings.DEFAULT_TTL_SECONDS),
    )
    client = app_client_factory(settings)
    container = client.app.state.container
    engine = container.db_engine()
    Base.metadata.create_all(engine)

    container.admin_auth_service().bootstrap_user(
        login="root",
        password="secret-123",
    )

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


def test_admin_login_rejects_invalid_credentials_without_disclosing_reason(app_client_factory, tmp_path) -> None:
    client = app_client_factory(
        Config(
            APP=AppSettings(),
            DATABASE=DatabaseSettings(URL=_database_url(tmp_path, "admin-auth-invalid.db")),
            SECURITY=SecuritySettings(SECRET_KEY="integration-secret"),
        )
    )
    container = client.app.state.container
    engine = container.db_engine()
    Base.metadata.create_all(engine)

    container.admin_auth_service().bootstrap_user(
        login="root",
        password="secret-123",
    )

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
