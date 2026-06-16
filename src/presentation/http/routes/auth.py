from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse

from application.admins.auth import authenticate_admin_user
from application.ports.security import PasswordHasher
from application.ports.unit_of_work import UnitOfWork
from application.settings import Config
from domain.admins.admin_user import AdminUser
from infrastructure.container import Container
from presentation.http.cookies import clear_admin_session_cookie, set_admin_session_cookie
from presentation.http.dependencies.auth import get_current_admin_user
from presentation.http.views.auth import render_admin_login_page

router = APIRouter()


@router.get("/admin/login", include_in_schema=False)
def admin_login_page() -> HTMLResponse:
    return HTMLResponse(render_admin_login_page())


@router.post("/admin/login", include_in_schema=False, response_model=None)
@inject
def admin_login(
    login: Annotated[str, Form(...)],
    password: Annotated[str, Form(...)],
    settings: Annotated[Config, Depends(Provide[Container.settings])],
    password_hasher: Annotated[PasswordHasher, Depends(Provide[Container.password_hasher])],
    uow: Annotated[UnitOfWork, Depends(Provide[Container.unit_of_work])],
) -> HTMLResponse | RedirectResponse:
    with uow:
        admin_user = authenticate_admin_user(
            uow,
            password_hasher,
            login=login,
            password=password,
        )
        if admin_user is None:
            return HTMLResponse(
                render_admin_login_page("Invalid credentials"), status_code=status.HTTP_401_UNAUTHORIZED
            )

        uow.commit()

    response = RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)
    set_admin_session_cookie(response, admin_user, settings)
    return response


@router.post("/admin/logout", include_in_schema=False, response_model=None)
@inject
def admin_logout(
    settings: Annotated[Config, Depends(Provide[Container.settings])],
) -> RedirectResponse:
    response = RedirectResponse("/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    clear_admin_session_cookie(response, settings)
    return response


@router.get("/admin", include_in_schema=False)
def admin_smoke(
    current_admin_user: Annotated[AdminUser, Depends(get_current_admin_user)],
) -> dict[str, str]:
    return {"status": "ok", "login": current_admin_user.login}
