from starlette.responses import Response

from application.settings import Config
from domain.admins.admin_user import AdminUser
from presentation.http.session import sign_admin_session


def set_admin_session_cookie(response: Response, admin_user: AdminUser, settings: Config) -> None:
    response.set_cookie(
        key=settings.ADMIN_SESSION.COOKIE_NAME,
        value=sign_admin_session(admin_user.id, settings.SECURITY.SECRET_KEY, settings.ADMIN_SESSION.TTL_SECONDS),
        httponly=True,
        secure=_cookie_is_secure(settings),
        samesite="lax",
        path="/",
        max_age=settings.ADMIN_SESSION.TTL_SECONDS,
    )


def clear_admin_session_cookie(response: Response, settings: Config) -> None:
    response.delete_cookie(
        key=settings.ADMIN_SESSION.COOKIE_NAME,
        path="/",
        httponly=True,
        secure=_cookie_is_secure(settings),
        samesite="lax",
    )


def _cookie_is_secure(settings: Config) -> bool:
    return settings.APP.ENVIRONMENT not in {"local", "test"}
