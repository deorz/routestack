from datetime import UTC, datetime

import pytest

from app_layer.admins.auth import AdminAuthService
from app_layer.admins.exceptions import AdminUserIncorrectPasswordError, AdminUserNotFoundError
from domain.admins.admin_user import AdminUser
from domain.shared.entity_id import new_entity_id
from tests.fakes import FakeUnitOfWork, InMemoryAdminUserRepository


class FakePasswordHasher:
    def hash_password(self, password: str) -> str:
        return f"hashed::{password}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        return password_hash == self.hash_password(password)


def test_bootstrap_admin_user_creates_admin_when_missing() -> None:
    repository = InMemoryAdminUserRepository()
    unit_of_work = FakeUnitOfWork(admins=repository)
    hasher = FakePasswordHasher()
    service = AdminAuthService(unit_of_work, hasher)

    admin_user = service.bootstrap_user(login="root", password="secret-123")

    assert admin_user.login == "root"
    assert admin_user.password_hash == "hashed::secret-123"
    assert repository.get_by_login("root") == admin_user
    assert unit_of_work.commits == 1


def test_bootstrap_admin_user_updates_existing_password_hash() -> None:
    repository = InMemoryAdminUserRepository()
    unit_of_work = FakeUnitOfWork(admins=repository)
    hasher = FakePasswordHasher()
    service = AdminAuthService(unit_of_work, hasher)
    existing_admin = AdminUser(login="root", password_hash="hashed::old-secret")
    repository.add(existing_admin)

    updated_admin = service.bootstrap_user(login="root", password="new-secret")

    assert updated_admin.id == existing_admin.id
    assert updated_admin.password_hash == "hashed::new-secret"
    assert repository.get_by_login("root") == updated_admin
    assert unit_of_work.commits == 1


def test_authenticate_admin_user_updates_last_login_at() -> None:
    repository = InMemoryAdminUserRepository()
    unit_of_work = FakeUnitOfWork(admins=repository)
    hasher = FakePasswordHasher()
    service = AdminAuthService(unit_of_work, hasher)
    existing_admin = AdminUser(login="root", password_hash="hashed::secret-123")
    repository.add(existing_admin)

    authenticated_admin = service.authenticate(
        login="root",
        password="secret-123",
    )

    assert authenticated_admin.last_login_at is not None
    assert repository.get_by_login("root") == authenticated_admin


def test_authenticate_admin_user_raises_not_found_for_missing_login() -> None:
    repository = InMemoryAdminUserRepository()
    unit_of_work = FakeUnitOfWork(admins=repository)
    hasher = FakePasswordHasher()
    service = AdminAuthService(unit_of_work, hasher)

    with pytest.raises(AdminUserNotFoundError):
        service.authenticate(login="missing", password="secret-123")


def test_authenticate_admin_user_raises_not_found_for_disabled_user() -> None:
    repository = InMemoryAdminUserRepository()
    unit_of_work = FakeUnitOfWork(admins=repository)
    hasher = FakePasswordHasher()
    service = AdminAuthService(unit_of_work, hasher)
    disabled_admin = AdminUser(login="root", password_hash="hashed::secret-123", disabled_at=datetime.now(tz=UTC))
    repository.add(disabled_admin)

    with pytest.raises(AdminUserNotFoundError):
        service.authenticate(login="root", password="secret-123")


def test_authenticate_admin_user_raises_incorrect_password() -> None:
    repository = InMemoryAdminUserRepository()
    unit_of_work = FakeUnitOfWork(admins=repository)
    hasher = FakePasswordHasher()
    service = AdminAuthService(unit_of_work, hasher)
    repository.add(AdminUser(login="root", password_hash="hashed::secret-123"))

    with pytest.raises(AdminUserIncorrectPasswordError):
        service.authenticate(login="root", password="wrong")


def test_get_enabled_user_returns_active_admin() -> None:
    repository = InMemoryAdminUserRepository()
    unit_of_work = FakeUnitOfWork(admins=repository)
    hasher = FakePasswordHasher()
    service = AdminAuthService(unit_of_work, hasher)
    admin = AdminUser(login="root", password_hash="hashed::secret-123")
    repository.add(admin)

    loaded = service.get_enabled_user(admin.id)

    assert loaded == admin


def test_get_enabled_user_raises_not_found_for_missing_user() -> None:
    repository = InMemoryAdminUserRepository()
    unit_of_work = FakeUnitOfWork(admins=repository)
    hasher = FakePasswordHasher()
    service = AdminAuthService(unit_of_work, hasher)

    with pytest.raises(AdminUserNotFoundError):
        service.get_enabled_user(new_entity_id())


def test_get_enabled_user_raises_not_found_for_disabled_user() -> None:
    repository = InMemoryAdminUserRepository()
    unit_of_work = FakeUnitOfWork(admins=repository)
    hasher = FakePasswordHasher()
    service = AdminAuthService(unit_of_work, hasher)
    disabled_admin = AdminUser(login="root", password_hash="hashed::secret-123", disabled_at=datetime.now(tz=UTC))
    repository.add(disabled_admin)

    with pytest.raises(AdminUserNotFoundError):
        service.get_enabled_user(disabled_admin.id)
