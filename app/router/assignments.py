from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.assignment_service import AssignmentService
from app.database import get_db
from app.dependencies import get_current_user
from app import models

router = APIRouter(
    prefix="/api/v1/projects/{project_id}/tasks/{task_id}/assignments",
    tags=["assignments"],
)
service = AssignmentService()


@router.get("")
def list_assignments(
    task_id: int,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return service.list_assignments(db, task_id, limit, offset)


@router.post("")
def assign_user(
    task_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    assignment = models.TaskAssignment(
        task_id=task_id, user_id=payload.get("user_id"), assigned_by=user.id
    )
    return service.assign_user(db, assignment)


@router.delete("/{user_id}")
def unassign_user(
    task_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    assignment = service.repo.get(db, task_id, user_id)
    service.unassign_user(db, assignment)
    return {"message": "assignment_removed"}
