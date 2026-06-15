from infrastructure.security.password_hasher import BcryptPasswordHasher


def test_bcrypt_password_hasher_round_trip_verification() -> None:
    hasher = BcryptPasswordHasher()

    password_hash = hasher.hash_password("secret-123")

    assert hasher.verify_password("secret-123", password_hash) is True


def test_bcrypt_password_hasher_rejects_wrong_password() -> None:
    hasher = BcryptPasswordHasher()
    password_hash = hasher.hash_password("secret-123")

    assert hasher.verify_password("wrong-password", password_hash) is False


def test_bcrypt_password_hasher_handles_long_passwords_without_truncation() -> None:
    hasher = BcryptPasswordHasher()
    password = "a" * 80 + "1"
    different_password = "a" * 80 + "2"

    password_hash = hasher.hash_password(password)

    assert hasher.verify_password(password, password_hash) is True
    assert hasher.verify_password(different_password, password_hash) is False


def test_bcrypt_password_hasher_returns_false_for_unknown_or_invalid_hash_scheme() -> None:
    hasher = BcryptPasswordHasher()

    assert hasher.verify_password("secret-123", "not-a-valid-hash") is False
    assert hasher.verify_password("secret-123", "other-scheme$abc") is False
