from pydantic import AwareDatetime, Field

from domain.shared.time import utc_now


class TimestampedMixin:
    created_at: AwareDatetime = Field(default_factory=utc_now)
    updated_at: AwareDatetime = Field(default_factory=utc_now)

    def _touch(self) -> None:
        self.updated_at = utc_now()
