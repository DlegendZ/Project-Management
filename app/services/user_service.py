from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app import models
from app.exceptions.errors import ResourceNotFoundError


class UserService:

    def __init__(self):
        self.repo = UserRepository()

    def ensure_found(self, resource):
        if not resource:
            raise ResourceNotFoundError("project_not_found")
        return resource

    def list_users(self, db: Session, limit: int = 20, offset: int = 0):
        users = self.repo.list_users(db, limit, offset)
        total = self.repo.count_users(db)

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": users,
        }

    def deactivate_user(self, db: Session, user: models.User):
        user = self.ensure_found(user)
        user = self.repo.deactivate_user(db, user)
        db.commit()
        db.refresh(user)
        return user

    def delete_user(self, db: Session, user: models.User):
        user = self.ensure_found(user)
        self.repo.delete_user(db, user)
        db.commit()

    def update_profile(
        self,
        db: Session,
        user: models.User,
        username: str | None = None,
        email: str | None = None,
        hashed_password: str | None = None,
    ):
        user = self.ensure_found(user)

        user = self.repo.update_profile(db, user, username, email, hashed_password)
        db.commit()
        db.refresh(user)
        return user
