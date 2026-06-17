from typing import Annotated

from fastapi import Header, HTTPException, status

IDEMPOTENCY_HEADER = "Idempotency-Key"


def parse_idempotency_key(
    idempotency_key: Annotated[str | None, Header(alias=IDEMPOTENCY_HEADER)] = None,
) -> str:
    if idempotency_key is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{IDEMPOTENCY_HEADER} header is required for mutating requests",
        )
    return idempotency_key
