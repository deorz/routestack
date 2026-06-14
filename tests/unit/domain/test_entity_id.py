import pytest

from domain.shared.entity_id import EntityId
from domain.shared.errors import DomainValidationError


def test_entity_id_round_trips_and_hashes_by_value() -> None:
    entity_id = EntityId.new()
    copied = EntityId.from_string(str(entity_id))

    assert copied == entity_id
    assert hash(copied) == hash(entity_id)
    assert str(copied) == str(entity_id)
    assert len({entity_id, copied}) == 1


def test_entity_id_rejects_invalid_string() -> None:
    with pytest.raises(DomainValidationError):
        EntityId.from_string("not-a-uuid")
