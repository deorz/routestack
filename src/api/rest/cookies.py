from starlette.responses import Response

from api.rest.session import sign_admin_session
from config import Config
from domain.admins.admin_user import AdminUser


def set_admin_session_cookie(response: Response, admin_user: AdminUser, settings: Config) -> None:
    response.set_cookie(
        key=settings.ADMIN_SESSION.COOKIE_NAME,
        value=sign_admin_session(admin_user.id, settings.SECURITY.SECRET_KEY, settings.ADMIN_SESSION.TTL_SECONDS),
        httponly=True,
        secure=settings.ADMIN_SESSION.COOKIE_SECURE,
        samesite="lax",
        path="/",
        max_age=settings.ADMIN_SESSION.TTL_SECONDS,
    )


def clear_admin_session_cookie(response: Response, settings: Config) -> None:
    response.delete_cookie(
        key=settings.ADMIN_SESSION.COOKIE_NAME,
        path="/",
        httponly=True,
        secure=settings.ADMIN_SESSION.COOKIE_SECURE,
        samesite="lax",
    )
