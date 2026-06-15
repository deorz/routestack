from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from application.admins.auth import authenticate_admin_user
from application.ports.security import PasswordHasher
from application.ports.unit_of_work import UnitOfWork
from application.settings import AppSettings
from domain.admins.admin_user import AdminUser
from infrastructure.container import Container
from presentation.http.session import ADMIN_SESSION_COOKIE_NAME, sign_admin_session, verify_admin_session

router = APIRouter()


@router.get("/admin/login", include_in_schema=False)
def admin_login_page() -> HTMLResponse:
    return HTMLResponse(_render_login_page())


@router.post("/admin/login", include_in_schema=False, response_model=None)
@inject
def admin_login(
    login: Annotated[str, Form(...)],
    password: Annotated[str, Form(...)],
    settings: Annotated[AppSettings, Depends(Provide[Container.settings])],
    password_hasher: Annotated[PasswordHasher, Depends(Provide[Container.password_hasher])],
    unit_of_work: Annotated[UnitOfWork, Depends(Provide[Container.unit_of_work])],
) -> HTMLResponse | RedirectResponse:
    with unit_of_work as transaction:
        admin_user = authenticate_admin_user(
            transaction,
            password_hasher,
            login=login,
            password=password,
        )
        if admin_user is None:
            return HTMLResponse(_render_login_page("Invalid credentials"), status_code=status.HTTP_401_UNAUTHORIZED)

        transaction.commit()

    response = RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)
    _set_admin_session_cookie(response, admin_user, settings)
    return response


@router.post("/admin/logout", include_in_schema=False, response_model=None)
@inject
def admin_logout(
    settings: Annotated[AppSettings, Depends(Provide[Container.settings])],
) -> RedirectResponse:
    response = RedirectResponse("/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(
        key=ADMIN_SESSION_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=_cookie_is_secure(settings.environment),
        samesite="lax",
    )
    return response


def get_current_admin_user(
    request: Request,
) -> AdminUser:
    container: Container = request.app.state.container
    settings = container.settings()
    unit_of_work = container.unit_of_work()
    session_token = request.cookies.get(ADMIN_SESSION_COOKIE_NAME)
    if not session_token:
        raise _unauthorized()

    admin_user_id = verify_admin_session(session_token, settings.secret_key)
    if admin_user_id is None:
        raise _unauthorized()

    with unit_of_work as transaction:
        admin_user = transaction.admins.get(admin_user_id)

    if admin_user is None or admin_user.disabled_at is not None:
        raise _unauthorized()

    return admin_user


@router.get("/admin", include_in_schema=False)
def admin_smoke(
    current_admin_user: Annotated[AdminUser, Depends(get_current_admin_user)],
) -> dict[str, str]:
    return {"status": "ok", "login": current_admin_user.login}


def _render_login_page(error_message: str | None = None) -> str:
    error_markup = f'<p role="alert">{error_message}</p>' if error_message else ""
    return (
        "<!doctype html>"
        '<html lang="en">'
        "<body>"
        f"{error_markup}"
        '<form method="post" action="/admin/login">'
        '<label>Login <input name="login" autocomplete="username"></label>'
        '<label>Password <input type="password" name="password" autocomplete="current-password"></label>'
        '<button type="submit">Sign in</button>'
        "</form>"
        "</body>"
        "</html>"
    )


def _set_admin_session_cookie(response: RedirectResponse, admin_user: AdminUser, settings: AppSettings) -> None:
    response.set_cookie(
        key=ADMIN_SESSION_COOKIE_NAME,
        value=sign_admin_session(admin_user.id, settings.secret_key),
        httponly=True,
        secure=_cookie_is_secure(settings.environment),
        samesite="lax",
        path="/",
    )


def _cookie_is_secure(environment: str) -> bool:
    return environment not in {"local", "test"}


def _unauthorized() -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
