from fastapi import HTTPException, Request, status

from domain.admins.admin_user import AdminUser
from infrastructure.container import Container
from presentation.http.session import verify_admin_session


def get_current_admin_user(request: Request) -> AdminUser:
    container: Container = request.app.state.container
    settings = container.settings()
    unit_of_work = container.unit_of_work()
    session_token = request.cookies.get(settings.admin_session_cookie_name)
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


def _unauthorized() -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
