import pytest

from app_layer.admins.auth import AdminAuthService
from tests.fakes import FakePasswordHasher, FakeUnitOfWork, InMemoryAdminUserRepository


@pytest.fixture
def password_hasher() -> FakePasswordHasher:
    return FakePasswordHasher()


@pytest.fixture
def admin_repository() -> InMemoryAdminUserRepository:
    return InMemoryAdminUserRepository()


@pytest.fixture
def unit_of_work(admin_repository: InMemoryAdminUserRepository) -> FakeUnitOfWork:
    return FakeUnitOfWork(admins=admin_repository)


@pytest.fixture
def admin_auth_service(unit_of_work: FakeUnitOfWork, password_hasher: FakePasswordHasher) -> AdminAuthService:
    return AdminAuthService(unit_of_work, password_hasher)
