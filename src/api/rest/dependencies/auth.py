from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, Request, status

from api.rest.session import verify_admin_session
from app_layer.admins.exceptions import AdminUserNotFoundError
from app_layer.ports.admins import AdminAuthenticationService
from config import Config
from containers import Container
from domain.admins.admin_user import AdminUser


@inject
def get_current_admin_user(
    request: Request,
    settings: Annotated[Config, Depends(Provide[Container.settings])],
    admin_auth_service: Annotated[AdminAuthenticationService, Depends(Provide[Container.admin_auth_service])],
) -> AdminUser:
    session_token = request.cookies.get(settings.ADMIN_SESSION.COOKIE_NAME)
    if not session_token:
        raise _unauthorized()

    admin_user_id = verify_admin_session(session_token, settings.SECURITY.SECRET_KEY)
    if admin_user_id is None:
        raise _unauthorized()

    try:
        return admin_auth_service.get_enabled_user(admin_user_id)
    except AdminUserNotFoundError:
        raise _unauthorized() from None


def _unauthorized() -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
