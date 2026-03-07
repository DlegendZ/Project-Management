from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional
from app.models.user import User


class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.get(User, user_id)

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        stmt = select(User).where(func.lower(User.email) == email.lower())
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        stmt = select(User).where(func.lower(User.username) == username.lower())
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def create(db: Session, **kwargs) -> User:
        user = User(**kwargs)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update(db: Session, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete(db: Session, user: User) -> None:
        db.delete(user)
        db.commit()

    @staticmethod
    def list_all(db: Session, limit: int = 20, offset: int = 0) -> tuple[list[User], int]:
        total = db.execute(select(func.count()).select_from(User)).scalar_one()
        stmt = select(User).limit(limit).offset(offset).order_by(User.id)
        users = db.execute(stmt).scalars().all()
        return list(users), total
