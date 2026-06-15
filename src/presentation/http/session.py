import hmac
from hashlib import sha256
from uuid import UUID

from domain.shared.entity_id import EntityId

ADMIN_SESSION_COOKIE_NAME = "routestack_admin_session"


def sign_admin_session(admin_user_id: EntityId, secret_key: str) -> str:
    payload = str(admin_user_id)
    signature = hmac.new(secret_key.encode("utf-8"), payload.encode("utf-8"), sha256).hexdigest()
    return f"{payload}.{signature}"


def verify_admin_session(session_token: str, secret_key: str) -> EntityId | None:
    try:
        payload, signature = session_token.rsplit(".", 1)
    except ValueError:
        return None

    expected_signature = hmac.new(secret_key.encode("utf-8"), payload.encode("utf-8"), sha256).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        return None

    try:
        return EntityId(UUID(payload))
    except ValueError:
        return None
