from datetime import UTC, datetime

from app_layer.admins.exceptions import AdminUserIncorrectPasswordError, AdminUserNotFoundError
from app_layer.ports.security import PasswordHasher
from app_layer.ports.unit_of_work import UnitOfWork
from domain.admins.admin_user import AdminUser
from domain.shared.entity_id import EntityId


class AdminAuthService:
    def __init__(self, unit_of_work: UnitOfWork, password_hasher: PasswordHasher) -> None:
        self._unit_of_work = unit_of_work
        self._password_hasher = password_hasher

    def bootstrap_user(self, *, login: str, password: str) -> AdminUser:
        password_hash = self._password_hasher.hash_password(password)

        with self._unit_of_work:
            admin_user = self._unit_of_work.admins.get_by_login(login)
            if admin_user is None:
                admin_user = AdminUser(login=login, password_hash=password_hash)
            else:
                admin_user.password_hash = password_hash

            self._unit_of_work.admins.add(admin_user)
            return admin_user

    def authenticate(self, *, login: str, password: str) -> AdminUser | None:
        with self._unit_of_work:
            admin_user = self._unit_of_work.admins.get_by_login(login)
            if admin_user is None or admin_user.disabled_at is not None:
                raise AdminUserNotFoundError

            if not self._password_hasher.verify_password(password, admin_user.password_hash):
                raise AdminUserIncorrectPasswordError

            admin_user.last_login_at = datetime.now(tz=UTC)
            self._unit_of_work.admins.add(admin_user)
            return admin_user

    def get_enabled_user(self, admin_user_id: EntityId) -> AdminUser | None:
        with self._unit_of_work:
            admin_user = self._unit_of_work.admins.get(admin_user_id)
            if admin_user is None or admin_user.disabled_at is not None:
                raise AdminUserNotFoundError

            return admin_user
