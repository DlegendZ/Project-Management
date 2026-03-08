from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.assignment import AssignRequest, AssignmentResponse
from app.services.assignment_service import AssignmentService

router = APIRouter(
    prefix="/projects/{project_id}/tasks/{task_id}/assignments", tags=["assignments"]
)


@router.get("", response_model=list[AssignmentResponse])
def list_assignments(
    project_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AssignmentService.list_assignments(db, project_id, task_id, current_user)


@router.post("", response_model=AssignmentResponse, status_code=201)
def assign_user(
    project_id: int,
    task_id: int,
    data: AssignRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AssignmentService.assign_user(
        db, project_id, task_id, current_user, data.user_id
    )


@router.delete("/{user_id}", status_code=204)
def unassign_user(
    project_id: int,
    task_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    AssignmentService.unassign_user(db, project_id, task_id, current_user, user_id)
