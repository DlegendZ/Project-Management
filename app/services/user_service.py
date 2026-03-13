from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.exceptions import (
    ConflictException,
    NotFoundException,
    BadRequestException,
    ForbiddenException,
)
from app.schemas.user import UpdateProfileRequest


class UserService:
    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str) -> User:
        if UserRepository.get_by_email(db, email):
            raise ConflictException("duplicate_email", "Email already registered")
        if UserRepository.get_by_username(db, username):
            raise ConflictException("duplicate_username", "Username already taken")
        hashed = AuthService.hash_password(password)
        return UserRepository.create(
            db, username=username, email=email, hashed_password=hashed
        )

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    @staticmethod
    def list_users(db: Session, limit: int, offset: int):
        return UserRepository.list_all(db, limit=limit, offset=offset)

    @staticmethod
    def update_profile(db: Session, user: User, data: UpdateProfileRequest) -> User:
        updates = {}
        if data.username and data.username != user.username:
            if UserRepository.get_by_username(db, data.username):
                raise ConflictException("duplicate_username", "Username already taken")
            updates["username"] = data.username
        if data.email and data.email.lower() != user.email.lower():
            if UserRepository.get_by_email(db, data.email):
                raise ConflictException("duplicate_email", "Email already registered")
            updates["email"] = data.email
        if data.new_password:
            if not data.current_password:
                raise BadRequestException(
                    "Current password is required to set a new password"
                )
            if not AuthService.verify_password(
                data.current_password, user.hashed_password
            ):
                raise BadRequestException("Current password is incorrect")
            if AuthService.verify_password(data.new_password, user.hashed_password):
                raise BadRequestException(
                    "New password must differ from current password"
                )
            updates["hashed_password"] = AuthService.hash_password(data.new_password)
        if updates:
            return UserRepository.update(db, user, **updates)
        return user

    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> User:
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise NotFoundException("User not found")
        return UserRepository.update(db, user, is_active=False)

    @staticmethod
    def activate_user(db: Session, user_id: int) -> User:
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise NotFoundException("User not found")
        return UserRepository.update(db, user, is_active=True)

    @staticmethod
    def search_users(db: Session, q: str) -> list[User]:
        return UserRepository.find_by_query(db, q)

    @staticmethod
    def delete_user(db: Session, user_id: int) -> None:
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise NotFoundException("User not found")
        UserRepository.delete(db, user)
