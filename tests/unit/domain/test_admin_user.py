from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from domain.admins.admin_user import AdminUser


def test_admin_user_trims_login_whitespace() -> None:
    admin_user = AdminUser(login="  root  ", password_hash="hash-123")

    assert admin_user.login == "root"


def test_admin_user_rejects_blank_login() -> None:
    with pytest.raises(ValidationError):
        AdminUser(login="   ", password_hash="hash-123")


def test_admin_user_rejects_blank_password_hash() -> None:
    with pytest.raises(ValidationError):
        AdminUser(login="root", password_hash="   ")


def test_admin_user_rejects_naive_created_at() -> None:
    with pytest.raises(ValidationError):
        AdminUser(
            login="root",
            password_hash="hash-123",
            created_at=datetime(2026, 6, 15, 12, 0, 0),
        )


def test_admin_user_accepts_explicit_timestamps() -> None:
    created_at = datetime(2026, 6, 15, 12, 0, 0, tzinfo=UTC)
    last_login_at = datetime(2026, 6, 15, 13, 0, 0, tzinfo=UTC)
    disabled_at = datetime(2026, 6, 15, 14, 0, 0, tzinfo=UTC)

    admin_user = AdminUser(
        login="root",
        password_hash="hash-123",
        created_at=created_at,
        last_login_at=last_login_at,
        disabled_at=disabled_at,
    )

    assert admin_user.created_at == created_at
    assert admin_user.last_login_at == last_login_at
    assert admin_user.disabled_at == disabled_at
