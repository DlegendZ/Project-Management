from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models.user import User
from app.schemas.user import UserResponse, UpdateProfileRequest
from app.schemas.common import PaginatedResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=PaginatedResponse[UserResponse])
def list_users(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    users, total = UserService.list_users(db, limit=limit, offset=offset)
    return PaginatedResponse(total=total, limit=limit, offset=offset, items=users)


@router.get("/me", response_model=UserResponse)
def get_own_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/search", response_model=list[UserResponse])
def search_users(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return UserService.search_users(db, q)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return UserService.get_user_by_id(db, user_id)


@router.patch("/me", response_model=UserResponse)
def update_profile(
    data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return UserService.update_profile(db, current_user, data)


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return UserService.deactivate_user(db, user_id)


@router.patch("/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: int,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return UserService.activate_user(db, user_id)


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    UserService.delete_user(db, user_id)
