from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.assignment_service import AssignmentService
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

service = AssignmentService()


@router.get("/mine")
def list_my_tasks(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return service.list_tasks_for_user(db, user.id, limit, offset)
