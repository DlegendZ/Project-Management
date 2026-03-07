from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app import models


class UserRepository:

    def get_by_id(self, db: Session, user_id: int) -> models.User | None:
        return db.get(models.User, user_id)

    def list_users(
        self, db: Session, limit: int = 20, offset: int = 0
    ) -> list[models.User]:
        stmt = select(models.User).limit(limit).offset(offset)
        return db.execute(stmt).scalars().all()

    def count_users(self, db: Session) -> int:
        stmt = select(func.count()).select_from(models.User)
        return db.execute(stmt).scalar_one()

    def deactivate_user(self, db: Session, user: models.User) -> models.User:
        user.is_active = False
        return user

    def delete_user(self, db: Session, user: models.User) -> None:
        db.delete(user)

    def update_profile(
        self,
        db: Session,
        user: models.User,
        username: str | None = None,
        email: str | None = None,
        hashed_password: str | None = None,
    ) -> models.User:
        if username is not None:
            user.username = username
        if email is not None:
            user.email = email
        if hashed_password is not None:
            user.hashed_password = hashed_password

        return user
