import pytest
from pydantic import ValidationError

from domain.clients.client import Client


def test_client_rejects_blank_display_name() -> None:
    with pytest.raises(ValidationError):
        Client(display_name="   ")


def test_client_rename_updates_display_name() -> None:
    client = Client(display_name="Alice")

    client.rename("  Bob  ")

    assert client.display_name == "Bob"


def test_client_soft_delete_disables_client() -> None:
    client = Client(display_name="Alice", enabled=True)

    client.soft_delete()

    assert client.enabled is False
    assert client.deleted_at is not None


def test_client_soft_delete_is_idempotent() -> None:
    client = Client(display_name="Alice", enabled=True)

    client.soft_delete()
    deleted_at = client.deleted_at

    client.soft_delete()

    assert client.enabled is False
    assert client.deleted_at == deleted_at
