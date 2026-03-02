from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app import models


class AdminRepository:

    # ------------------------
    # User Management
    # ------------------------

    def get_user_by_id_repo(self, db: Session, user_id: int):
        return db.get(models.User, user_id)

    def list_users_repo(self, db: Session, limit: int = 20, offset: int = 0):
        stmt = select(models.User).limit(limit).offset(offset)
        return db.execute(stmt).scalars().all()

    def create_user(self, db: Session, user: models.User):
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def deactivate_user_repo(self, db: Session, user: models.User):
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user

    def delete_user_repo(self, db: Session, user: models.User):
        db.delete(user)
        db.commit()

    def update_user_profile_repo(
        self,
        db: Session,
        user: models.User,
        username: str | None = None,
        email: str | None = None,
        hashed_password: str | None = None,
    ):
        if username is not None:
            user.username = username
        if email is not None:
            user.email = email
        if hashed_password is not None:
            user.hashed_password = hashed_password

        db.commit()
        db.refresh(user)
        return user

    # ------------------------
    # Project Management
    # ------------------------

    def create_project_repo(self, db: Session, project: models.Project):
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    def get_project_by_id_repo(self, db: Session, project_id: int):
        return db.get(models.Project, project_id)

    def list_projects_repo(self, db: Session, limit: int = 20, offset: int = 0):
        stmt = select(models.Project).limit(limit).offset(offset)
        return db.execute(stmt).scalars().all()

    def update_project_repo(
        self,
        db: Session,
        project: models.Project,
        name: str | None = None,
        description: str | None = None,
    ):
        pass


