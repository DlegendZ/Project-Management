from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, Literal
from datetime import date
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.task import TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.schemas.common import PaginatedResponse
from app.services.task_service import TaskService

router = APIRouter(tags=["tasks"])


@router.get("/tasks/mine", response_model=PaginatedResponse[TaskResponse])
def list_my_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    sort_by: Literal["created_at", "due_date", "priority", "updated_at"] = "created_at",
    sort_dir: Literal["asc", "desc"] = "desc",
    limit: int = Query(20, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tasks, total = TaskService.list_my_tasks(
        db,
        current_user,
        status=status,
        priority=priority,
        sort_by=sort_by,
        sort_dir=sort_dir,
        limit=limit,
        offset=offset,
    )
    return PaginatedResponse(
        total=total, limit=limit, offset=offset, items=_build_task_responses(tasks)
    )


@router.get(
    "/projects/{project_id}/tasks", response_model=PaginatedResponse[TaskResponse]
)
def list_tasks(
    project_id: int,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    assignee_id: Optional[int] = None,
    due_date_from: Optional[date] = None,
    due_date_to: Optional[date] = None,
    is_overdue: Optional[bool] = None,
    created_by: Optional[int] = None,
    q: Optional[str] = None,
    sort_by: Literal["created_at", "due_date", "priority", "updated_at"] = "created_at",
    sort_dir: Literal["asc", "desc"] = "desc",
    limit: int = Query(20, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tasks, total = TaskService.list_tasks(
        db,
        project_id,
        current_user,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        due_date_from=due_date_from,
        due_date_to=due_date_to,
        is_overdue=is_overdue,
        created_by=created_by,
        q=q,
        sort_by=sort_by,
        sort_dir=sort_dir,
        limit=limit,
        offset=offset,
    )
    return PaginatedResponse(
        total=total, limit=limit, offset=offset, items=_build_task_responses(tasks)
    )


@router.post(
    "/projects/{project_id}/tasks", response_model=TaskResponse, status_code=201
)
def create_task(
    project_id: int,
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = TaskService.create_task(db, project_id, current_user, data)
    return _build_task_response(task)


@router.get("/projects/{project_id}/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    project_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = TaskService.get_task(db, project_id, task_id, current_user)
    return _build_task_response(task)


@router.patch("/projects/{project_id}/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    project_id: int,
    task_id: int,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = TaskService.update_task(db, project_id, task_id, current_user, data)
    return _build_task_response(task)


@router.delete("/projects/{project_id}/tasks/{task_id}", status_code=204)
def delete_task(
    project_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    TaskService.delete_task(db, project_id, task_id, current_user)


def _build_task_response(task) -> TaskResponse:
    from app.schemas.task import AssigneeInfo

    assignees = [
        AssigneeInfo(
            id=a.assignee.id, username=a.assignee.username, email=a.assignee.email
        )
        for a in task.assignments
        if a.assignee
    ]
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        project_id=task.project_id,
        created_by=task.created_by,
        created_at=task.created_at,
        updated_at=task.updated_at,
        assignees=assignees,
    )


def _build_task_responses(tasks) -> list[TaskResponse]:
    return [_build_task_response(t) for t in tasks]
