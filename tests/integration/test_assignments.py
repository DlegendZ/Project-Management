import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.conftest import create_test_user, get_auth_headers
from app.models.project_member import ProjectMember


def _add_member(db, project_id, user_id):
    m = ProjectMember(project_id=project_id, user_id=user_id)
    db.add(m)
    db.commit()


def test_assign_user_to_task_success(client: TestClient, user_headers: dict, test_project, test_task, db: Session):
    assignee = create_test_user(db, username="assignee1", email="assignee1@example.com")
    db.commit()
    _add_member(db, test_project.id, assignee.id)
    resp = client.post(
        f"/api/v1/projects/{test_project.id}/tasks/{test_task.id}/assignments",
        headers=user_headers,
        json={"user_id": assignee.id},
    )
    assert resp.status_code == 201
    assert resp.json()["user_id"] == assignee.id


def test_assign_user_duplicate_returns_409(client: TestClient, user_headers: dict, test_project, test_task, db: Session):
    assignee = create_test_user(db, username="dupas", email="dupas@example.com")
    db.commit()
    _add_member(db, test_project.id, assignee.id)
    client.post(
        f"/api/v1/projects/{test_project.id}/tasks/{test_task.id}/assignments",
        headers=user_headers,
        json={"user_id": assignee.id},
    )
    resp = client.post(
        f"/api/v1/projects/{test_project.id}/tasks/{test_task.id}/assignments",
        headers=user_headers,
        json={"user_id": assignee.id},
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "duplicate_assignment"


def test_assign_non_member_returns_403(client: TestClient, user_headers: dict, test_project, test_task, db: Session):
    non_member = create_test_user(db, username="nonmemas", email="nonmemas@example.com")
    db.commit()
    resp = client.post(
        f"/api/v1/projects/{test_project.id}/tasks/{test_task.id}/assignments",
        headers=user_headers,
        json={"user_id": non_member.id},
    )
    assert resp.status_code == 403


def test_unassign_user_success(client: TestClient, user_headers: dict, test_project, test_task, db: Session):
    assignee = create_test_user(db, username="unasign", email="unasign@example.com")
    db.commit()
    _add_member(db, test_project.id, assignee.id)
    client.post(
        f"/api/v1/projects/{test_project.id}/tasks/{test_task.id}/assignments",
        headers=user_headers,
        json={"user_id": assignee.id},
    )
    resp = client.delete(
        f"/api/v1/projects/{test_project.id}/tasks/{test_task.id}/assignments/{assignee.id}",
        headers=user_headers,
    )
    assert resp.status_code == 204


def test_list_assignments(client: TestClient, user_headers: dict, test_project, test_task):
    resp = client.get(
        f"/api/v1/projects/{test_project.id}/tasks/{test_task.id}/assignments",
        headers=user_headers,
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_assign_as_non_owner_returns_403(client: TestClient, test_project, test_task, db: Session):
    member = create_test_user(db, username="memonly", email="memonly@example.com")
    assignee = create_test_user(db, username="assigneet", email="assigneet@example.com")
    db.commit()
    _add_member(db, test_project.id, member.id)
    _add_member(db, test_project.id, assignee.id)
    headers = get_auth_headers(client, email="memonly@example.com")
    resp = client.post(
        f"/api/v1/projects/{test_project.id}/tasks/{test_task.id}/assignments",
        headers=headers,
        json={"user_id": assignee.id},
    )
    assert resp.status_code == 403
