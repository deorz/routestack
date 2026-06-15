import hmac
from hashlib import sha256
from uuid import UUID

import pytest

from domain.shared.entity_id import EntityId
from presentation.http import session as session_module
from presentation.http.session import sign_admin_session, verify_admin_session


def test_sign_admin_session_embeds_expiry_timestamp(monkeypatch) -> None:
    monkeypatch.setattr(session_module.time, "time", lambda: 1_700_000_000)

    admin_user_id = EntityId(UUID("11111111-1111-1111-1111-111111111111"))

    session_token = sign_admin_session(admin_user_id, "secret-key", ttl_seconds=600)
    payload, _signature = session_token.rsplit(".", 1)

    assert payload == f"{admin_user_id}.1700000600"


def test_verify_admin_session_accepts_valid_token_before_expiry(monkeypatch) -> None:
    monkeypatch.setattr(session_module.time, "time", lambda: 1_700_000_000)

    admin_user_id = EntityId(UUID("22222222-2222-2222-2222-222222222222"))
    session_token = sign_admin_session(admin_user_id, "secret-key", ttl_seconds=600)

    monkeypatch.setattr(session_module.time, "time", lambda: 1_700_000_500)

    assert verify_admin_session(session_token, "secret-key") == admin_user_id


def test_verify_admin_session_rejects_expired_token(monkeypatch) -> None:
    monkeypatch.setattr(session_module.time, "time", lambda: 1_700_000_000)

    admin_user_id = EntityId(UUID("33333333-3333-3333-3333-333333333333"))
    session_token = sign_admin_session(admin_user_id, "secret-key", ttl_seconds=60)

    monkeypatch.setattr(session_module.time, "time", lambda: 1_700_000_061)

    assert verify_admin_session(session_token, "secret-key") is None


def test_verify_admin_session_rejects_tampered_token(monkeypatch) -> None:
    monkeypatch.setattr(session_module.time, "time", lambda: 1_700_000_000)

    admin_user_id = EntityId(UUID("44444444-4444-4444-4444-444444444444"))
    session_token = sign_admin_session(admin_user_id, "secret-key", ttl_seconds=600)
    tampered_token = session_token[:-1] + ("0" if session_token[-1] != "0" else "1")

    assert verify_admin_session(tampered_token, "secret-key") is None


@pytest.mark.parametrize(
    "payload",
    [
        "not-a-uuid.1700000600",
        "55555555-5555-5555-5555-555555555555.not-a-timestamp",
    ],
)
def test_verify_admin_session_rejects_invalid_payload(monkeypatch, payload: str) -> None:
    monkeypatch.setattr(session_module.time, "time", lambda: 1_700_000_000)

    signature = hmac.new(b"secret-key", payload.encode("utf-8"), sha256).hexdigest()
    session_token = f"{payload}.{signature}"

    assert verify_admin_session(session_token, "secret-key") is None
