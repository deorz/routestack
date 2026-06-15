from starlette.responses import Response

from application.settings import AppSettings
from domain.admins.admin_user import AdminUser
from presentation.http.session import sign_admin_session


def set_admin_session_cookie(response: Response, admin_user: AdminUser, settings: AppSettings) -> None:
    response.set_cookie(
        key=settings.admin_session_cookie_name,
        value=sign_admin_session(admin_user.id, settings.secret_key, settings.admin_session_ttl_seconds),
        httponly=True,
        secure=_cookie_is_secure(settings),
        samesite="lax",
        path="/",
        max_age=settings.admin_session_ttl_seconds,
    )


def clear_admin_session_cookie(response: Response, settings: AppSettings) -> None:
    response.delete_cookie(
        key=settings.admin_session_cookie_name,
        path="/",
        httponly=True,
        secure=_cookie_is_secure(settings),
        samesite="lax",
    )


def _cookie_is_secure(settings: AppSettings) -> bool:
    return settings.environment not in AppSettings.NON_STRONG_SECRET_ENVIRONMENTS
