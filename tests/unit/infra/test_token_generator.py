from infra.security.tokens import Sha256AccessTokenGenerator


def test_token_generator_produces_distinct_tokens() -> None:
    gen = Sha256AccessTokenGenerator()
    raw1, hashed1 = gen.generate()
    raw2, hashed2 = gen.generate()

    assert raw1 != raw2
    assert hashed1 != hashed2
    assert len(raw1) >= 43  # 32 bytes base64url
    assert hashed1.startswith("routestack-sha256$")


def test_token_verification_accepts_valid_token() -> None:
    gen = Sha256AccessTokenGenerator()
    raw, hashed = gen.generate()

    assert gen.verify(raw, hashed) is True


def test_token_verification_rejects_tampered_token() -> None:
    gen = Sha256AccessTokenGenerator()
    raw, hashed = gen.generate()

    assert gen.verify(raw + "tampered", hashed) is False


def test_token_verification_rejects_unknown_scheme() -> None:
    gen = Sha256AccessTokenGenerator()
    raw, hashed = gen.generate()

    # Strip the scheme prefix to simulate an unknown hash format
    bare_hash = hashed.removeprefix("routestack-sha256$")
    assert gen.verify(raw, bare_hash) is False


def test_token_generator_satisfies_port() -> None:
    from app_layer.ports.security import AccessTokenGenerator

    assert isinstance(Sha256AccessTokenGenerator(), AccessTokenGenerator)
