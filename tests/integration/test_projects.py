import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.conftest import create_test_user, get_auth_headers


def test_create_project_success(client: TestClient, user_headers: dict):
    resp = client.post(
        "/api/v1/projects", headers=user_headers, json={"name": "New Project"}
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "New Project"


def test_list_projects_only_returns_accessible(
    client: TestClient, user_headers: dict, test_project
):
    resp = client.get("/api/v1/projects", headers=user_headers)
    assert resp.status_code == 200
    ids = [p["id"] for p in resp.json()["items"]]
    assert test_project.id in ids


def test_get_project_success(client: TestClient, user_headers: dict, test_project):
    resp = client.get(f"/api/v1/projects/{test_project.id}", headers=user_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == test_project.id


def test_get_project_not_found_returns_404(client: TestClient, user_headers: dict):
    resp = client.get("/api/v1/projects/99999", headers=user_headers)
    assert resp.status_code == 404


def test_update_project_as_owner(client: TestClient, user_headers: dict, test_project):
    resp = client.patch(
        f"/api/v1/projects/{test_project.id}",
        headers=user_headers,
        json={"name": "Updated"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated"


def test_update_project_as_non_owner_returns_403(
    client: TestClient, db: Session, test_project
):
    other = create_test_user(db, username="notowner", email="notowner@example.com")
    db.commit()
    headers = get_auth_headers(client, email="notowner@example.com")
    resp = client.patch(
        f"/api/v1/projects/{test_project.id}", headers=headers, json={"name": "Hack"}
    )
    assert resp.status_code in (403, 404)


def test_archive_project(client: TestClient, user_headers: dict, test_project):
    resp = client.patch(
        f"/api/v1/projects/{test_project.id}/archive", headers=user_headers
    )
    assert resp.status_code == 200
    assert resp.json()["is_archived"] is True


def test_delete_project_as_owner(
    client: TestClient, user_headers: dict, db: Session, test_user
):
    from app.models.project import Project
    from app.models.project_member import ProjectMember

    p = Project(name="ToDelete", owner_id=test_user.id)
    db.add(p)
    db.flush()
    db.add(ProjectMember(project_id=p.id, user_id=test_user.id))
    db.commit()
    resp = client.delete(f"/api/v1/projects/{p.id}", headers=user_headers)
    assert resp.status_code == 204


def test_add_member_to_project(
    client: TestClient, user_headers: dict, test_project, db: Session
):
    new_user = create_test_user(db, username="newmem", email="newmem@example.com")
    db.commit()
    resp = client.post(
        f"/api/v1/projects/{test_project.id}/members",
        headers=user_headers,
        json={"user_id": new_user.id},
    )
    assert resp.status_code == 201


def test_add_member_duplicate_returns_409(
    client: TestClient, user_headers: dict, test_project, test_user
):
    # test_user is already a member (owner)
    resp = client.post(
        f"/api/v1/projects/{test_project.id}/members",
        headers=user_headers,
        json={"user_id": test_user.id},
    )
    assert resp.status_code == 409


def test_remove_member_from_project(
    client: TestClient, user_headers: dict, test_project, db: Session
):
    mem = create_test_user(db, username="torem", email="torem@example.com")
    db.commit()
    client.post(
        f"/api/v1/projects/{test_project.id}/members",
        headers=user_headers,
        json={"user_id": mem.id},
    )
    resp = client.delete(
        f"/api/v1/projects/{test_project.id}/members/{mem.id}", headers=user_headers
    )
    assert resp.status_code == 204


def test_list_members(client: TestClient, user_headers: dict, test_project):
    resp = client.get(
        f"/api/v1/projects/{test_project.id}/members", headers=user_headers
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_admin_sees_all_projects(client: TestClient, admin_headers: dict, test_project):
    resp = client.get("/api/v1/projects", headers=admin_headers)
    assert resp.status_code == 200
    ids = [p["id"] for p in resp.json()["items"]]
    assert test_project.id in ids
