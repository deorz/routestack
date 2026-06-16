import pytest
from pydantic import ValidationError

from application.settings import AdminSessionSettings, AppSettings, Config, DatabaseSettings, SecuritySettings


def _clear_settings_environment(monkeypatch) -> None:
    monkeypatch.delenv("ROUTESTACK_APP_NAME", raising=False)
    monkeypatch.delenv("ROUTESTACK_APP_ENVIRONMENT", raising=False)
    monkeypatch.delenv("ROUTESTACK_DATABASE_URL", raising=False)
    monkeypatch.delenv("ROUTESTACK_SECURITY_SECRET_KEY", raising=False)
    monkeypatch.delenv("ROUTESTACK_ADMIN_SESSION_COOKIE_NAME", raising=False)
    monkeypatch.delenv("ROUTESTACK_ADMIN_SESSION_TTL_SECONDS", raising=False)
    monkeypatch.delenv("ROUTESTACK_SERVER_HOST", raising=False)
    monkeypatch.delenv("ROUTESTACK_SERVER_PORT", raising=False)


def test_settings_have_local_defaults(monkeypatch) -> None:
    _clear_settings_environment(monkeypatch)

    settings = Config()

    assert settings.APP.NAME == "RouteStack"
    assert settings.APP.ENVIRONMENT == "local"
    assert settings.DATABASE.URL == "sqlite:///./routestack.db"
    assert settings.SECURITY.SECRET_KEY == SecuritySettings.DEFAULT_SECRET_KEY
    assert settings.ADMIN_SESSION.TTL_SECONDS == AdminSessionSettings.DEFAULT_TTL_SECONDS
    assert settings.ADMIN_SESSION.COOKIE_NAME == "routestack_admin_session"
    assert settings.SERVER.HOST == "0.0.0.0"
    assert settings.SERVER.PORT == 8000


def test_settings_read_category_environment_prefixes(monkeypatch) -> None:
    _clear_settings_environment(monkeypatch)
    monkeypatch.setenv("ROUTESTACK_APP_NAME", "InjectedStack")
    monkeypatch.setenv("ROUTESTACK_APP_ENVIRONMENT", "test")
    monkeypatch.setenv("ROUTESTACK_DATABASE_URL", "sqlite:///./test.db")
    monkeypatch.setenv("ROUTESTACK_SECURITY_SECRET_KEY", "test-secret")
    monkeypatch.setenv("ROUTESTACK_ADMIN_SESSION_COOKIE_NAME", "admin_cookie")
    monkeypatch.setenv("ROUTESTACK_ADMIN_SESSION_TTL_SECONDS", "60")
    monkeypatch.setenv("ROUTESTACK_SERVER_HOST", "127.0.0.1")
    monkeypatch.setenv("ROUTESTACK_SERVER_PORT", "9000")

    settings = Config()

    assert AppSettings(NAME="InjectedStack", ENVIRONMENT="test") == settings.APP
    assert DatabaseSettings(URL="sqlite:///./test.db") == settings.DATABASE
    assert SecuritySettings(SECRET_KEY="test-secret") == settings.SECURITY
    assert AdminSessionSettings(TTL_SECONDS=60, COOKIE_NAME="admin_cookie") == settings.ADMIN_SESSION
    assert settings.SERVER.HOST == "127.0.0.1"
    assert settings.SERVER.PORT == 9000


def test_settings_reject_blank_admin_session_cookie_name(monkeypatch) -> None:
    _clear_settings_environment(monkeypatch)

    with pytest.raises(ValidationError, match="String should have at least 1 character"):
        AdminSessionSettings(COOKIE_NAME="")
