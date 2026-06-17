from base64 import urlsafe_b64encode
from hashlib import sha256

import bcrypt

_HASH_SCHEME_PREFIX = "routestack-bcrypt-sha256$"


class BcryptPasswordHasher:
    def hash_password(self, password: str) -> str:
        password_digest = self._sha256_password_digest(password)
        bcrypt_hash = bcrypt.hashpw(password_digest, bcrypt.gensalt())
        return f"{_HASH_SCHEME_PREFIX}{bcrypt_hash.decode('ascii')}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        if not password_hash.startswith(_HASH_SCHEME_PREFIX):
            return False

        bcrypt_hash = password_hash.removeprefix(_HASH_SCHEME_PREFIX)
        try:
            bcrypt_hash_bytes = bcrypt_hash.encode("ascii")
        except UnicodeEncodeError:
            return False

        try:
            password_digest = self._sha256_password_digest(password)
            return bcrypt.checkpw(password_digest, bcrypt_hash_bytes)
        except (TypeError, ValueError):
            return False

    def _sha256_password_digest(self, password: str) -> bytes:
        return urlsafe_b64encode(sha256(password.encode("utf-8")).digest()).rstrip(b"=")
