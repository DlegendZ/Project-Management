import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.conftest import create_test_user


def test_register_success(client: TestClient):
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "username": "reguser",
            "email": "reg@example.com",
            "password": "Secure1Pass",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "reguser"
    assert "hashed_password" not in data
    assert "password" not in data


def test_register_duplicate_email_returns_409(client: TestClient, test_user):
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "username": "other99",
            "email": "test@example.com",
            "password": "Secure1Pass",
        },
    )
    assert resp.status_code == 409


def test_register_duplicate_username_returns_409(client: TestClient, test_user):
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "unique99@example.com",
            "password": "Secure1Pass",
        },
    )
    assert resp.status_code == 409


def test_register_weak_password_returns_422(client: TestClient):
    resp = client.post(
        "/api/v1/auth/register",
        json={"username": "weakpass", "email": "weak@example.com", "password": "short"},
    )
    assert resp.status_code == 422


def test_register_missing_fields_returns_422(client: TestClient):
    resp = client.post("/api/v1/auth/register", json={"username": "incomplete"})
    assert resp.status_code == 422


def test_login_with_valid_credentials_returns_tokens(client: TestClient, test_user):
    resp = client.post(
        "/api/v1/auth/login", json={"email": "test@example.com", "password": "Test1234"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_wrong_password_returns_401(client: TestClient, test_user):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "WrongPass1"},
    )
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "invalid_credentials"


def test_login_with_unknown_email_returns_401(client: TestClient):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "Test1234"},
    )
    assert resp.status_code == 401


def test_login_inactive_account_returns_403(client: TestClient, db: Session):
    user = create_test_user(
        db, username="inactive", email="inactive@example.com", password="Test1234"
    )
    user.is_active = False
    db.commit()
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "inactive@example.com", "password": "Test1234"},
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "account_disabled"


def test_get_me_with_valid_token(client: TestClient, user_headers: dict):
    resp = client.get("/api/v1/auth/me", headers=user_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"


def test_get_me_without_token_returns_401(client: TestClient):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_refresh_token_success(client: TestClient, test_user):
    login = client.post(
        "/api/v1/auth/login", json={"email": "test@example.com", "password": "Test1234"}
    )
    refresh_token = login.json()["refresh_token"]
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_refresh_with_invalid_token_returns_401(client: TestClient):
    resp = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": "invalid.token.here"}
    )
    assert resp.status_code == 401


def test_logout_invalidates_token(client: TestClient, test_user, user_headers: dict):
    # Logout
    resp = client.post("/api/v1/auth/logout", headers=user_headers)
    assert resp.status_code == 204
    # Old token should be invalid
    resp2 = client.get("/api/v1/auth/me", headers=user_headers)
    assert resp2.status_code == 401
