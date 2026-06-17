from hashlib import sha256
from secrets import token_urlsafe

_SCHEME_PREFIX = "routestack-sha256$"
_ENTROPY_BYTES = 32


class Sha256AccessTokenGenerator:
    def generate(self) -> tuple[str, str]:
        raw = token_urlsafe(_ENTROPY_BYTES)
        hashed = self._hash(raw)
        return raw, hashed

    def verify(self, raw_token: str, hashed_token: str) -> bool:
        if not hashed_token.startswith(_SCHEME_PREFIX):
            return False
        return self._hash(raw_token) == hashed_token

    @staticmethod
    def _hash(raw_token: str) -> str:
        digest = sha256(raw_token.encode("utf-8")).hexdigest()
        return f"{_SCHEME_PREFIX}{digest}"
