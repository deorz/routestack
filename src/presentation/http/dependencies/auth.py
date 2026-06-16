from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, Request, status

from application.ports.unit_of_work import UnitOfWork
from application.settings import Config
from domain.admins.admin_user import AdminUser
from infrastructure.container import Container
from presentation.http.session import verify_admin_session


@inject
def get_current_admin_user(
    request: Request,
    settings: Annotated[Config, Depends(Provide[Container.settings])],
    unit_of_work: Annotated[UnitOfWork, Depends(Provide[Container.unit_of_work])],
) -> AdminUser:
    session_token = request.cookies.get(settings.ADMIN_SESSION.COOKIE_NAME)
    if not session_token:
        raise _unauthorized()

    admin_user_id = verify_admin_session(session_token, settings.SECURITY.SECRET_KEY)
    if admin_user_id is None:
        raise _unauthorized()

    with unit_of_work as transaction:
        admin_user = transaction.admins.get(admin_user_id)

    if admin_user is None or admin_user.disabled_at is not None:
        raise _unauthorized()

    return admin_user


def _unauthorized() -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
