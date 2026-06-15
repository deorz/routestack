from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse

from application.admins.services import AdminAuthService
from application.settings import AppSettings
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
    settings: Annotated[AppSettings, Depends(Provide[Container.settings])],
    auth_service: Annotated[AdminAuthService, Depends(Provide[Container.admin_auth_service])],
) -> HTMLResponse | RedirectResponse:
    admin_user = auth_service.authenticate(login=login, password=password)
    if admin_user is None:
        return HTMLResponse(render_admin_login_page("Invalid credentials"), status_code=status.HTTP_401_UNAUTHORIZED)

    response = RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)
    set_admin_session_cookie(response, admin_user, settings)
    return response


@router.post("/admin/logout", include_in_schema=False, response_model=None)
@inject
def admin_logout(
    settings: Annotated[AppSettings, Depends(Provide[Container.settings])],
) -> RedirectResponse:
    response = RedirectResponse("/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    clear_admin_session_cookie(response, settings)
    return response


@router.get("/admin", include_in_schema=False)
def admin_smoke(
    current_admin_user: Annotated[AdminUser, Depends(get_current_admin_user)],
) -> dict[str, str]:
    return {"status": "ok", "login": current_admin_user.login}
