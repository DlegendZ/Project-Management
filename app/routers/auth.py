from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    AccessTokenResponse,
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.exceptions import UnauthorizedException

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = UserService.create_user(
        db, username=data.username, email=data.email, password=data.password
    )
    return user


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = UserRepository.get_by_email(db, data.email)
    if not user or not AuthService.verify_password(data.password, user.hashed_password):
        raise UnauthorizedException("invalid_credentials", "Invalid credentials")
    if not user.is_active:
        from app.exceptions import ForbiddenException

        raise ForbiddenException("account_disabled", "Account is deactivated")
    access_token = AuthService.create_access_token(
        user.id, user.role.value, user.token_version
    )
    refresh_token = AuthService.create_refresh_token(user.id, user.token_version)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh_token(data: RefreshRequest, db: Session = Depends(get_db)):
    payload = AuthService.decode_refresh_token(data.refresh_token)
    user_id = int(payload["sub"])
    token_version = payload.get("token_version", 0)
    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise UnauthorizedException("invalid_token", "User not found")
    if user.token_version != token_version:
        raise UnauthorizedException("invalid_token", "Token has been invalidated")
    if not user.is_active:
        from app.exceptions import ForbiddenException

        raise ForbiddenException("account_disabled", "Account is deactivated")
    access_token = AuthService.create_access_token(
        user.id, user.role.value, user.token_version
    )
    return AccessTokenResponse(access_token=access_token)


@router.post("/logout", status_code=204)
def logout(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    # Increment token_version to invalidate all existing tokens
    UserRepository.update(
        db, current_user, token_version=current_user.token_version + 1
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
