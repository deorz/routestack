import time
import uuid
from secrets import randbits
from uuid import UUID

EntityId = UUID


def new_entity_id() -> EntityId:
    stdlib_uuid7 = getattr(uuid, "uuid7", None)
    if stdlib_uuid7 is not None:
        return stdlib_uuid7()

    return _uuid7_from_unix_ms(time.time_ns() // 1_000_000)


def _uuid7_from_unix_ms(unix_ms: int) -> EntityId:
    timestamp = (unix_ms & ((1 << 48) - 1)) << 80
    version = 0x7 << 76
    rand_a = randbits(12) << 64
    variant = 0b10 << 62
    rand_b = randbits(62)

    return UUID(int=timestamp | version | rand_a | variant | rand_b)
