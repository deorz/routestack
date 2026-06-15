from dataclasses import dataclass, field

from application.admins.auth import authenticate_admin_user, bootstrap_admin_user
from application.ports.repositories import AdminUserRepository
from domain.admins.admin_user import AdminUser
from domain.shared.entity_id import EntityId


class FakePasswordHasher:
    def hash_password(self, password: str) -> str:
        return f"hashed::{password}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        return password_hash == self.hash_password(password)


@dataclass
class InMemoryAdminUserRepository:
    admins: dict[EntityId, AdminUser] = field(default_factory=dict)

    def add(self, admin_user: AdminUser) -> None:
        self.admins[admin_user.id] = admin_user

    def get(self, admin_user_id: EntityId) -> AdminUser | None:
        return self.admins.get(admin_user_id)

    def get_by_login(self, login: str) -> AdminUser | None:
        for admin_user in self.admins.values():
            if admin_user.login == login:
                return admin_user

        return None


@dataclass
class FakeUnitOfWork:
    admins: AdminUserRepository


def test_bootstrap_admin_user_creates_admin_when_missing() -> None:
    repository = InMemoryAdminUserRepository()
    unit_of_work = FakeUnitOfWork(admins=repository)
    hasher = FakePasswordHasher()

    admin_user = bootstrap_admin_user(unit_of_work, hasher, login="  root  ", password="secret-123")

    assert admin_user.login == "root"
    assert admin_user.password_hash == "hashed::secret-123"
    assert repository.get_by_login("root") == admin_user


def test_bootstrap_admin_user_updates_existing_password_hash() -> None:
    repository = InMemoryAdminUserRepository()
    unit_of_work = FakeUnitOfWork(admins=repository)
    hasher = FakePasswordHasher()
    existing_admin = AdminUser(login="root", password_hash="hashed::old-secret")
    repository.add(existing_admin)

    updated_admin = bootstrap_admin_user(unit_of_work, hasher, login="root", password="new-secret")

    assert updated_admin.id == existing_admin.id
    assert updated_admin.password_hash == "hashed::new-secret"
    assert repository.get_by_login("root") == updated_admin


def test_authenticate_admin_user_updates_last_login_at() -> None:
    repository = InMemoryAdminUserRepository()
    unit_of_work = FakeUnitOfWork(admins=repository)
    hasher = FakePasswordHasher()
    existing_admin = AdminUser(login="root", password_hash="hashed::secret-123")
    repository.add(existing_admin)

    authenticated_admin = authenticate_admin_user(
        unit_of_work,
        hasher,
        login="root",
        password="secret-123",
    )

    assert authenticated_admin is not None
    assert authenticated_admin.last_login_at is not None
    assert repository.get_by_login("root") == authenticated_admin


def test_authenticate_admin_user_rejects_invalid_credentials() -> None:
    repository = InMemoryAdminUserRepository()
    unit_of_work = FakeUnitOfWork(admins=repository)
    hasher = FakePasswordHasher()
    repository.add(AdminUser(login="root", password_hash="hashed::secret-123"))

    assert authenticate_admin_user(unit_of_work, hasher, login="root", password="wrong") is None
    assert authenticate_admin_user(unit_of_work, hasher, login="missing", password="secret-123") is None
