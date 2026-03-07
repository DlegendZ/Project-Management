from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.task_service import TaskService
from app.repositories.project_repository import ProjectRepository
from app.database import get_db
from app.dependencies import get_current_user
from app import models

router = APIRouter(prefix="/api/v1/projects/{project_id}/tasks", tags=["tasks"])
service = TaskService()
project_repo = ProjectRepository()


@router.get("")
def list_tasks(
    project_id: int,
    limit: int = 20,
    offset: int = 0,
    status: str | None = None,
    priority: str | None = None,
    assignee_id: int | None = None,
    due_date_from: str | None = None,
    due_date_to: str | None = None,
    sort_by: str | None = None,
    sort_dir: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return service.list_tasks(
        db,
        project_id,
        limit=limit,
        offset=offset,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        due_date_from=due_date_from,
        due_date_to=due_date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
        q=q,
    )


@router.get("/{task_id}")
def get_task(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    task = service.repo.get_by_id(db, task_id)
    return task


@router.post("")
def create_task(
    project_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    task = models.Task(**payload, project_id=project_id, created_by=user.id)
    return service.create_task(db, task)


@router.patch("/{task_id}")
def update_task(
    project_id: int,
    task_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    task = service.repo.get_by_id(db, task_id)
    project = project_repo.get_by_id(db, project_id)
    return service.update_task(db, user, task, project, **payload)


@router.delete("/{task_id}")
def delete_task(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    task = service.repo.get_by_id(db, task_id)
    project = project_repo.get_by_id(db, project_id)
    service.delete_task(db, user, task, project)
    return {"message": "task_deleted"}
