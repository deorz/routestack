from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse

from api.rest.cookies import clear_admin_session_cookie, set_admin_session_cookie
from api.rest.dependencies.auth import get_current_admin_user
from api.rest.views.auth import render_admin_login_page
from app_layer.admins.exceptions import AdminUserIncorrectPasswordError, AdminUserNotFoundError
from app_layer.ports.admins import AdminAuthenticationService
from config import Config
from containers import Container
from domain.admins.admin_user import AdminUser

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
    service: Annotated[AdminAuthenticationService, Depends(Provide[Container.admin_auth_service])],
) -> HTMLResponse | RedirectResponse:
    try:
        admin_user = service.authenticate(login=login, password=password)
    except (AdminUserNotFoundError, AdminUserIncorrectPasswordError):
        return HTMLResponse(render_admin_login_page("Invalid credentials"), status_code=status.HTTP_401_UNAUTHORIZED)

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
