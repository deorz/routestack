import pytest
from pydantic import ValidationError

from application.settings import DEFAULT_ADMIN_SESSION_TTL_SECONDS, DEFAULT_SECRET_KEY, AppSettings


def _clear_settings_environment(monkeypatch) -> None:
    monkeypatch.delenv("ROUTESTACK_APP_NAME", raising=False)
    monkeypatch.delenv("ROUTESTACK_ENVIRONMENT", raising=False)
    monkeypatch.delenv("ROUTESTACK_DATABASE_URL", raising=False)
    monkeypatch.delenv("ROUTESTACK_SECRET_KEY", raising=False)
    monkeypatch.delenv("ROUTESTACK_ADMIN_SESSION_TTL_SECONDS", raising=False)
    monkeypatch.delenv("ROUTESTACK_SERVER_HOST", raising=False)
    monkeypatch.delenv("ROUTESTACK_SERVER_PORT", raising=False)


def test_settings_have_secure_local_defaults(monkeypatch) -> None:
    _clear_settings_environment(monkeypatch)

    settings = AppSettings()

    assert settings.app_name == "RouteStack"
    assert settings.environment == "local"
    assert settings.database_url == "sqlite:///./routestack.db"
    assert settings.secret_key == DEFAULT_SECRET_KEY
    assert settings.admin_session_ttl_seconds == DEFAULT_ADMIN_SESSION_TTL_SECONDS
    assert settings.server_host == "0.0.0.0"
    assert settings.server_port == 8000


@pytest.mark.parametrize("environment", ["local", "test"])
def test_settings_allow_default_secret_in_local_and_test(monkeypatch, environment: str) -> None:
    _clear_settings_environment(monkeypatch)

    settings = AppSettings(environment=environment)

    assert settings.secret_key == DEFAULT_SECRET_KEY


@pytest.mark.parametrize("environment", ["production", "staging"])
def test_settings_reject_default_secret_in_non_local_test_environments(monkeypatch, environment: str) -> None:
    _clear_settings_environment(monkeypatch)

    with pytest.raises(ValidationError, match="secret_key"):
        AppSettings(environment=environment)


@pytest.mark.parametrize("environment", ["production", "staging"])
def test_settings_reject_weak_secret_in_non_local_test_environments(monkeypatch, environment: str) -> None:
    _clear_settings_environment(monkeypatch)

    with pytest.raises(ValidationError, match="secret_key"):
        AppSettings(environment=environment, secret_key="too-short")


@pytest.mark.parametrize("environment", ["production", "staging"])
def test_settings_accept_strong_secret_in_non_local_test_environments(monkeypatch, environment: str) -> None:
    _clear_settings_environment(monkeypatch)

    settings = AppSettings(environment=environment, secret_key="super-strong-secret-key-0123456789abcdef")

    assert settings.secret_key == "super-strong-secret-key-0123456789abcdef"
