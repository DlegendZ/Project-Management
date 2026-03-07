import pytest
import time
from jose import jwt
from app.services.auth_service import AuthService, ALGORITHM
from app.config import settings
from app.exceptions import UnauthorizedException


def test_hash_password_returns_hashed_string():
    hashed = AuthService.hash_password("MyPassword1")
    assert hashed != "MyPassword1"
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")


def test_verify_password_correct():
    hashed = AuthService.hash_password("MyPassword1")
    assert AuthService.verify_password("MyPassword1", hashed) is True


def test_verify_password_wrong():
    hashed = AuthService.hash_password("MyPassword1")
    assert AuthService.verify_password("WrongPass1", hashed) is False


def test_create_access_token_contains_claims():
    token = AuthService.create_access_token(42, "user", 0)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "42"
    assert payload["role"] == "user"
    assert payload["type"] == "access"
    assert payload["token_version"] == 0


def test_create_refresh_token_contains_claims():
    token = AuthService.create_refresh_token(42, 1)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "42"
    assert payload["type"] == "refresh"
    assert payload["token_version"] == 1


def test_decode_access_token_valid():
    token = AuthService.create_access_token(7, "admin", 3)
    payload = AuthService.decode_access_token(token)
    assert payload["sub"] == "7"
    assert payload["role"] == "admin"


def test_decode_access_token_wrong_type_raises():
    token = AuthService.create_refresh_token(7, 0)
    with pytest.raises(UnauthorizedException) as exc:
        AuthService.decode_access_token(token)
    assert exc.value.code == "invalid_token"


def test_decode_refresh_token_wrong_type_raises():
    token = AuthService.create_access_token(7, "user", 0)
    with pytest.raises(UnauthorizedException) as exc:
        AuthService.decode_refresh_token(token)
    assert exc.value.code == "invalid_token"


def test_decode_access_token_invalid_signature_raises():
    with pytest.raises(UnauthorizedException) as exc:
        AuthService.decode_access_token("invalid.token.here")
    assert exc.value.code == "invalid_token"


def test_decode_expired_token_raises():
    from datetime import datetime, timedelta, timezone
    payload = {
        "sub": "1",
        "role": "user",
        "token_version": 0,
        "type": "access",
        "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
        "iat": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
    with pytest.raises(UnauthorizedException) as exc:
        AuthService.decode_access_token(token)
    assert exc.value.code == "token_expired"
