import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.conftest import create_test_user
from app.models.user import UserRole


def test_list_users_as_admin_returns_200(client: TestClient, admin_headers: dict):
    resp = client.get("/api/v1/users", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data


def test_list_users_as_regular_user_returns_403(client: TestClient, user_headers: dict):
    resp = client.get("/api/v1/users", headers=user_headers)
    assert resp.status_code == 403


def test_get_user_by_id_as_admin(client: TestClient, admin_headers: dict, test_user):
    resp = client.get(f"/api/v1/users/{test_user.id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == test_user.id


def test_deactivate_user_as_admin(client: TestClient, admin_headers: dict, db: Session):
    user = create_test_user(db, username="todeactivate2", email="deact2@example.com")
    db.commit()
    resp = client.patch(f"/api/v1/users/{user.id}/deactivate", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


def test_deactivate_user_as_regular_user_returns_403(
    client: TestClient, user_headers: dict, db: Session
):
    user = create_test_user(db, username="todeact3", email="deact3@example.com")
    db.commit()
    resp = client.patch(f"/api/v1/users/{user.id}/deactivate", headers=user_headers)
    assert resp.status_code == 403


def test_delete_user_as_admin(client: TestClient, admin_headers: dict, db: Session):
    user = create_test_user(db, username="todelet", email="todel@example.com")
    db.commit()
    resp = client.delete(f"/api/v1/users/{user.id}", headers=admin_headers)
    assert resp.status_code == 204


def test_update_own_profile(client: TestClient, user_headers: dict, test_user):
    resp = client.patch(
        "/api/v1/users/me", headers=user_headers, json={"username": "updatedname"}
    )
    assert resp.status_code == 200
    assert resp.json()["username"] == "updatedname"


def test_password_not_in_response(client: TestClient, user_headers: dict):
    resp = client.get("/api/v1/auth/me", headers=user_headers)
    data = resp.json()
    assert "password" not in data
    assert "hashed_password" not in data
