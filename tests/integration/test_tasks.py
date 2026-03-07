import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.conftest import create_test_user, get_auth_headers
from app.models.project import Project
from app.models.project_member import ProjectMember


def test_create_task_as_member(client: TestClient, user_headers: dict, test_project):
    resp = client.post(
        f"/api/v1/projects/{test_project.id}/tasks",
        headers=user_headers,
        json={"title": "New Task", "status": "todo", "priority": "low"},
    )
    assert resp.status_code == 201
    assert resp.json()["title"] == "New Task"


def test_create_task_as_non_member_returns_403_or_404(client: TestClient, db: Session, test_project):
    other = create_test_user(db, username="nonmem", email="nonmem@example.com")
    db.commit()
    headers = get_auth_headers(client, email="nonmem@example.com")
    resp = client.post(
        f"/api/v1/projects/{test_project.id}/tasks",
        headers=headers,
        json={"title": "Hack", "status": "todo", "priority": "low"},
    )
    assert resp.status_code in (403, 404)


def test_get_task_success(client: TestClient, user_headers: dict, test_project, test_task):
    resp = client.get(f"/api/v1/projects/{test_project.id}/tasks/{test_task.id}", headers=user_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == test_task.id
    assert "assignees" in resp.json()


def test_list_tasks_with_pagination(client: TestClient, user_headers: dict, test_project, test_task):
    resp = client.get(f"/api/v1/projects/{test_project.id}/tasks?limit=1&offset=0", headers=user_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["limit"] == 1
    assert len(data["items"]) <= 1


def test_list_tasks_filtered_by_status_returns_correct_items(
    client: TestClient, user_headers: dict, test_project, test_task
):
    resp = client.get(f"/api/v1/projects/{test_project.id}/tasks?status=todo", headers=user_headers)
    assert resp.status_code == 200
    for item in resp.json()["items"]:
        assert item["status"] == "todo"


def test_list_tasks_filtered_by_priority(client: TestClient, user_headers: dict, test_project, test_task):
    resp = client.get(f"/api/v1/projects/{test_project.id}/tasks?priority=medium", headers=user_headers)
    assert resp.status_code == 200
    for item in resp.json()["items"]:
        assert item["priority"] == "medium"


def test_list_tasks_search_by_keyword(client: TestClient, user_headers: dict, test_project):
    # Create a distinctively named task
    client.post(
        f"/api/v1/projects/{test_project.id}/tasks",
        headers=user_headers,
        json={"title": "SearchableTask_XYZ", "status": "todo", "priority": "low"},
    )
    resp = client.get(f"/api/v1/projects/{test_project.id}/tasks?q=SearchableTask_XYZ", headers=user_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert any("SearchableTask_XYZ" in item["title"] for item in data["items"])


def test_list_tasks_sort_by_due_date(client: TestClient, user_headers: dict, test_project):
    resp = client.get(f"/api/v1/projects/{test_project.id}/tasks?sort_by=due_date&sort_dir=asc", headers=user_headers)
    assert resp.status_code == 200


def test_update_task_as_owner(client: TestClient, user_headers: dict, test_project, test_task):
    resp = client.patch(
        f"/api/v1/projects/{test_project.id}/tasks/{test_task.id}",
        headers=user_headers,
        json={"status": "in_progress"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"


def test_delete_task_as_creator(client: TestClient, user_headers: dict, test_project, db: Session, test_user):
    from app.models.task import Task, TaskStatus, TaskPriority
    t = Task(title="Delete me", project_id=test_project.id, created_by=test_user.id,
             status=TaskStatus.todo, priority=TaskPriority.low)
    db.add(t)
    db.commit()
    resp = client.delete(f"/api/v1/projects/{test_project.id}/tasks/{t.id}", headers=user_headers)
    assert resp.status_code == 204


def test_list_my_tasks(client: TestClient, user_headers: dict):
    resp = client.get("/api/v1/tasks/mine", headers=user_headers)
    assert resp.status_code == 200
    assert "items" in resp.json()


def test_create_task_past_due_date_returns_400(client: TestClient, user_headers: dict, test_project):
    past = (date.today() - timedelta(days=1)).isoformat()
    resp = client.post(
        f"/api/v1/projects/{test_project.id}/tasks",
        headers=user_headers,
        json={"title": "Past Due", "status": "todo", "priority": "low", "due_date": past},
    )
    assert resp.status_code == 400
