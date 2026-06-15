from application.admins.auth import bootstrap_admin_user
from application.settings import AppSettings
from infrastructure.db import Base


def _database_url(tmp_path, name: str) -> str:
    return f"sqlite:///{tmp_path / name}"


def test_admin_login_flow_sets_session_cookie_and_protects_admin_route(app_client_factory, tmp_path) -> None:
    client = app_client_factory(
        AppSettings(
            app_name="InjectedStack",
            database_url=_database_url(tmp_path, "admin-auth-flow.db"),
            environment="test",
            secret_key="integration-secret",
        )
    )
    container = client.app.state.container
    engine = container.db_engine()
    Base.metadata.create_all(engine)

    with container.unit_of_work() as unit_of_work:
        bootstrap_admin_user(
            unit_of_work,
            container.password_hasher(),
            login="root",
            password="secret-123",
        )
        unit_of_work.commit()

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
    assert "routestack_admin_session" in response.headers.get("set-cookie", "")

    protected = client.get("/admin")
    assert protected.status_code == 200
    assert protected.json() == {"status": "ok", "login": "root"}

    logout = client.post("/admin/logout", follow_redirects=False)
    assert logout.status_code == 303
    assert logout.headers["location"] == "/admin/login"
    assert "routestack_admin_session" in logout.headers.get("set-cookie", "")
    assert "Max-Age=0" in logout.headers.get("set-cookie", "")

    after_logout = client.get("/admin")
    assert after_logout.status_code == 401


def test_admin_login_rejects_invalid_credentials_without_disclosing_reason(app_client_factory, tmp_path) -> None:
    client = app_client_factory(
        AppSettings(
            database_url=_database_url(tmp_path, "admin-auth-invalid.db"),
            environment="test",
            secret_key="integration-secret",
        )
    )
    container = client.app.state.container
    engine = container.db_engine()
    Base.metadata.create_all(engine)

    with container.unit_of_work() as unit_of_work:
        bootstrap_admin_user(
            unit_of_work,
            container.password_hasher(),
            login="root",
            password="secret-123",
        )
        unit_of_work.commit()

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
