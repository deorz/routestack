from datetime import UTC, datetime

import pytest

from app_layer.admins.auth import AdminAuthService
from app_layer.admins.exceptions import AdminUserIncorrectPasswordError, AdminUserNotFoundError
from domain.admins.admin_user import AdminUser
from domain.shared.entity_id import new_entity_id
from tests.fakes import FakeUnitOfWork, InMemoryAdminUserRepository


def test_bootstrap_admin_user_creates_admin_when_missing(
    admin_auth_service: AdminAuthService,
    admin_repository: InMemoryAdminUserRepository,
    unit_of_work: FakeUnitOfWork,
) -> None:
    admin_user = admin_auth_service.bootstrap_user(login="root", password="secret-123")

    assert admin_user.login == "root"
    assert admin_user.password_hash == "hashed::secret-123"
    assert admin_repository.get_by_login("root") == admin_user
    assert unit_of_work.commits == 1


def test_bootstrap_admin_user_updates_existing_password_hash(
    admin_auth_service: AdminAuthService,
    admin_repository: InMemoryAdminUserRepository,
    unit_of_work: FakeUnitOfWork,
) -> None:
    existing_admin = AdminUser(login="root", password_hash="hashed::old-secret")
    admin_repository.add(existing_admin)

    updated_admin = admin_auth_service.bootstrap_user(login="root", password="new-secret")

    assert updated_admin.id == existing_admin.id
    assert updated_admin.password_hash == "hashed::new-secret"
    assert admin_repository.get_by_login("root") == updated_admin
    assert unit_of_work.commits == 1


def test_authenticate_admin_user_updates_last_login_at(
    admin_auth_service: AdminAuthService,
    admin_repository: InMemoryAdminUserRepository,
) -> None:
    existing_admin = AdminUser(login="root", password_hash="hashed::secret-123")
    admin_repository.add(existing_admin)

    authenticated_admin = admin_auth_service.authenticate(login="root", password="secret-123")

    assert authenticated_admin.last_login_at is not None
    assert admin_repository.get_by_login("root") == authenticated_admin


def test_authenticate_admin_user_raises_not_found_for_missing_login(
    admin_auth_service: AdminAuthService,
) -> None:
    with pytest.raises(AdminUserNotFoundError):
        admin_auth_service.authenticate(login="missing", password="secret-123")


def test_authenticate_admin_user_raises_not_found_for_disabled_user(
    admin_auth_service: AdminAuthService,
    admin_repository: InMemoryAdminUserRepository,
) -> None:
    disabled_admin = AdminUser(login="root", password_hash="hashed::secret-123", disabled_at=datetime.now(tz=UTC))
    admin_repository.add(disabled_admin)

    with pytest.raises(AdminUserNotFoundError):
        admin_auth_service.authenticate(login="root", password="secret-123")


def test_authenticate_admin_user_raises_incorrect_password(
    admin_auth_service: AdminAuthService,
    admin_repository: InMemoryAdminUserRepository,
) -> None:
    admin_repository.add(AdminUser(login="root", password_hash="hashed::secret-123"))

    with pytest.raises(AdminUserIncorrectPasswordError):
        admin_auth_service.authenticate(login="root", password="wrong")


def test_get_enabled_user_returns_active_admin(
    admin_auth_service: AdminAuthService,
    admin_repository: InMemoryAdminUserRepository,
) -> None:
    admin = AdminUser(login="root", password_hash="hashed::secret-123")
    admin_repository.add(admin)

    loaded = admin_auth_service.get_enabled_user(admin.id)

    assert loaded == admin


def test_get_enabled_user_raises_not_found_for_missing_user(
    admin_auth_service: AdminAuthService,
) -> None:
    with pytest.raises(AdminUserNotFoundError):
        admin_auth_service.get_enabled_user(new_entity_id())


def test_get_enabled_user_raises_not_found_for_disabled_user(
    admin_auth_service: AdminAuthService,
    admin_repository: InMemoryAdminUserRepository,
) -> None:
    disabled_admin = AdminUser(login="root", password_hash="hashed::secret-123", disabled_at=datetime.now(tz=UTC))
    admin_repository.add(disabled_admin)

    with pytest.raises(AdminUserNotFoundError):
        admin_auth_service.get_enabled_user(disabled_admin.id)
