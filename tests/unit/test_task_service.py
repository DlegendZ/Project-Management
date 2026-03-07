import pytest
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.services.task_service import TaskService
from app.services.project_service import ProjectService
from app.schemas.task import TaskCreate, TaskUpdate
from app.schemas.project import ProjectCreate
from app.models.task import TaskStatus, TaskPriority
from app.exceptions import ForbiddenException, NotFoundException, BadRequestException
from tests.conftest import create_test_user


def setup_project_and_task(db):
    owner = create_test_user(db, username="towner", email="towner@example.com")
    db.commit()
    project = ProjectService.create_project(db, owner, ProjectCreate(name="Task Project"))
    task = TaskService.create_task(
        db, project.id, owner, TaskCreate(title="A Task", status=TaskStatus.todo, priority=TaskPriority.medium)
    )
    return owner, project, task


def test_create_task_success(db: Session):
    owner, project, task = setup_project_and_task(db)
    assert task.id is not None
    assert task.title == "A Task"
    assert task.project_id == project.id
    assert task.created_by == owner.id


def test_create_task_past_due_date_raises(db: Session):
    owner = create_test_user(db, username="towner2", email="towner2@example.com")
    db.commit()
    project = ProjectService.create_project(db, owner, ProjectCreate(name="P2"))
    with pytest.raises(BadRequestException):
        TaskService.create_task(
            db, project.id, owner,
            TaskCreate(title="Bad Task", due_date=date.today() - timedelta(days=1),
                       status=TaskStatus.todo, priority=TaskPriority.low)
        )


def test_get_task_not_found_raises(db: Session):
    owner = create_test_user(db, username="towner3", email="towner3@example.com")
    db.commit()
    project = ProjectService.create_project(db, owner, ProjectCreate(name="P3"))
    with pytest.raises(NotFoundException):
        TaskService.get_task(db, project.id, 99999, owner)


def test_delete_task_by_non_member_raises(db: Session):
    owner = create_test_user(db, username="towner4", email="towner4@example.com")
    other = create_test_user(db, username="other4t", email="other4t@example.com")
    db.commit()
    project = ProjectService.create_project(db, owner, ProjectCreate(name="P4"))
    task = TaskService.create_task(
        db, project.id, owner, TaskCreate(title="Del Task", status=TaskStatus.todo, priority=TaskPriority.low)
    )
    with pytest.raises((ForbiddenException, NotFoundException)):
        TaskService.delete_task(db, project.id, task.id, other)


def test_list_tasks_filter_by_status(db: Session):
    owner = create_test_user(db, username="towner5", email="towner5@example.com")
    db.commit()
    project = ProjectService.create_project(db, owner, ProjectCreate(name="P5"))
    TaskService.create_task(db, project.id, owner, TaskCreate(title="Todo", status=TaskStatus.todo, priority=TaskPriority.low))
    TaskService.create_task(db, project.id, owner, TaskCreate(title="Done", status=TaskStatus.done, priority=TaskPriority.low))
    tasks, total = TaskService.list_tasks(db, project.id, owner, status=TaskStatus.todo)
    assert total == 1
    assert tasks[0].title == "Todo"


def test_list_tasks_search(db: Session):
    owner = create_test_user(db, username="towner6", email="towner6@example.com")
    db.commit()
    project = ProjectService.create_project(db, owner, ProjectCreate(name="P6"))
    TaskService.create_task(db, project.id, owner, TaskCreate(title="Fix login bug", status=TaskStatus.todo, priority=TaskPriority.low))
    TaskService.create_task(db, project.id, owner, TaskCreate(title="Add dashboard", status=TaskStatus.todo, priority=TaskPriority.low))
    tasks, total = TaskService.list_tasks(db, project.id, owner, q="login")
    assert total == 1
    assert "login" in tasks[0].title.lower()
