from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, Request, status

from application.admins.services import AdminAuthService
from application.settings import AppSettings
from domain.admins.admin_user import AdminUser
from infrastructure.container import Container
from presentation.http.session import verify_admin_session


@inject
def get_current_admin_user(
    request: Request,
    settings: Annotated[AppSettings, Depends(Provide[Container.settings])],
    auth_service: Annotated[AdminAuthService, Depends(Provide[Container.admin_auth_service])],
) -> AdminUser:
    session_token = request.cookies.get(settings.admin_session.cookie_name)
    if not session_token:
        raise _unauthorized()

    admin_user_id = verify_admin_session(session_token, settings.security.secret_key)
    if admin_user_id is None:
        raise _unauthorized()

    admin_user = auth_service.get_active_admin(admin_user_id)
    if admin_user is None:
        raise _unauthorized()

    return admin_user


def _unauthorized() -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
