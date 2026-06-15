import hmac
import time
from hashlib import sha256
from uuid import UUID

from domain.shared.entity_id import EntityId


def sign_admin_session(admin_user_id: EntityId, secret_key: str, ttl_seconds: int) -> str:
    expires_at = int(time.time()) + ttl_seconds
    payload = f"{admin_user_id}.{expires_at}"
    signature = hmac.new(secret_key.encode("utf-8"), payload.encode("utf-8"), sha256).hexdigest()
    return f"{payload}.{signature}"


def verify_admin_session(session_token: str, secret_key: str) -> EntityId | None:
    try:
        payload, signature = session_token.rsplit(".", 1)
        admin_user_id, expires_at = payload.rsplit(".", 1)
    except ValueError:
        return None

    expected_signature = hmac.new(secret_key.encode("utf-8"), payload.encode("utf-8"), sha256).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        return None

    try:
        if int(expires_at) <= int(time.time()):
            return None

        return EntityId(UUID(admin_user_id))
    except ValueError:
        return None
