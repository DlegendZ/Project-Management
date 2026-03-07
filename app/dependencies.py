from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.user import User, UserRole
from app.exceptions import UnauthorizedException, ForbiddenException
from app.services.auth_service import AuthService

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise UnauthorizedException("token_required", "Authentication required")

    token = credentials.credentials
    payload = AuthService.decode_access_token(token)
    user_id = payload.get("sub")
    token_version = payload.get("token_version", 0)

    from app.repositories.user_repository import UserRepository
    user = UserRepository.get_by_id(db, int(user_id))
    if not user:
        raise UnauthorizedException("invalid_token", "User not found")

    if user.token_version != token_version:
        raise UnauthorizedException("invalid_token", "Token has been invalidated")

    if not user.is_active:
        raise ForbiddenException("account_disabled", "Account is deactivated")

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.admin:
        raise ForbiddenException("permission_denied", "Admin access required")
    return current_user
