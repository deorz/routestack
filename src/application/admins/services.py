from collections.abc import Callable

from application.admins.auth import authenticate_admin_user
from application.ports.security import PasswordHasher
from application.ports.unit_of_work import UnitOfWork
from domain.admins.admin_user import AdminUser
from domain.shared.entity_id import EntityId


class AdminAuthService:
    def __init__(
        self,
        unit_of_work_factory: Callable[[], UnitOfWork],
        password_hasher: PasswordHasher,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._password_hasher = password_hasher

    def authenticate(self, *, login: str, password: str) -> AdminUser | None:
        with self._unit_of_work_factory() as transaction:
            admin_user = authenticate_admin_user(
                transaction,
                self._password_hasher,
                login=login,
                password=password,
            )
            if admin_user is None:
                return None

            transaction.commit()
            return admin_user

    def get_active_admin(self, admin_user_id: EntityId) -> AdminUser | None:
        with self._unit_of_work_factory() as transaction:
            admin_user = transaction.admins.get(admin_user_id)

        if admin_user is None or admin_user.disabled_at is not None:
            return None

        return admin_user
