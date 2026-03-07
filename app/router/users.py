from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.database import get_db
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/api/v1/users", tags=["users"])
service = UserService()


@router.get("")
def list_users(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return service.list_users(db, limit, offset)


@router.patch("/me")
def update_profile(
    payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    return service.update_profile(
        db,
        user,
        payload.get("username"),
        payload.get("email"),
        payload.get("hashed_password"),
    )


@router.patch("/{user_id}/deactivate")
def deactivate_user(
    user_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)
):
    user = service.repo.get_by_id(db, user_id)
    return service.deactivate_user(db, user)


@router.delete("/{user_id}")
def delete_user(
    user_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)
):
    user = service.repo.get_by_id(db, user_id)
    service.delete_user(db, user)
    return {"message": "user_deleted"}
