from pydantic import AwareDatetime, Field

from domain.shared.time import utc_now


class DatetimeMixin:
    created_at: AwareDatetime = Field(default_factory=utc_now)
    updated_at: AwareDatetime = Field(default_factory=utc_now)

    def _record_update(self) -> None:
        self.updated_at = utc_now()
