from application.ports.security import PasswordHasher
from application.ports.unit_of_work import UnitOfWork
from domain.admins.admin_user import AdminUser
from domain.shared.errors import DomainValidationError
from domain.shared.time import utc_now


def bootstrap_admin_user(
    unit_of_work: UnitOfWork,
    password_hasher: PasswordHasher,
    *,
    login: str,
    password: str,
) -> AdminUser:
    normalized_login = _normalize_login(login)
    password_value = _require_password(password)
    password_hash = password_hasher.hash_password(password_value)

    admin_user = unit_of_work.admins.get_by_login(normalized_login)
    if admin_user is None:
        admin_user = AdminUser(login=normalized_login, password_hash=password_hash)
    else:
        admin_user.password_hash = password_hash

    unit_of_work.admins.add(admin_user)
    return admin_user


def authenticate_admin_user(
    unit_of_work: UnitOfWork,
    password_hasher: PasswordHasher,
    *,
    login: str,
    password: str,
) -> AdminUser | None:
    normalized_login = _normalize_login_for_auth(login)
    password_value = _normalize_password_for_auth(password)
    if normalized_login is None or password_value is None:
        return None

    admin_user = unit_of_work.admins.get_by_login(normalized_login)
    if admin_user is None or admin_user.disabled_at is not None:
        return None

    if not password_hasher.verify_password(password_value, admin_user.password_hash):
        return None

    admin_user.last_login_at = utc_now()
    unit_of_work.admins.add(admin_user)
    return admin_user


def _normalize_login(login: str) -> str:
    if not isinstance(login, str):
        raise DomainValidationError("login must be a string")

    normalized_login = login.strip()
    if not normalized_login:
        raise DomainValidationError("login cannot be blank")

    return normalized_login


def _normalize_login_for_auth(login: str) -> str | None:
    if not isinstance(login, str):
        return None

    normalized_login = login.strip()
    if not normalized_login:
        return None

    return normalized_login


def _require_password(password: str) -> str:
    if not isinstance(password, str):
        raise DomainValidationError("password must be a string")

    if not password.strip():
        raise DomainValidationError("password cannot be blank")

    return password


def _normalize_password_for_auth(password: str) -> str | None:
    if not isinstance(password, str):
        return None

    if not password.strip():
        return None

    return password
