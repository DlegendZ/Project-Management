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
        if name is not None :
            project.name = name
        if description is not None :
            project.description = description
        
        db.commit()
        db.refresh(project)
        return project
    
    def archive_project_repo(self, db: Session, project: models.Project):
        project.is_archived = True
        db.commit()
        db.refresh(project)
        return project
    
    def delete_project_repo(self, db: Session, project: models.Project):
        db.delete(project)
        db.commit()

    def add_member_to_project_repo(self, db: Session, ProjectMember: models.ProjectMember):
        db.add(ProjectMember)
        db.commit()
        db.refresh(ProjectMember)
        return ProjectMember
    
    def get_project_member_by_id_repo(self, db: Session, user_id: int, project_id: int):
        return db.get(models.ProjectMember, (project_id, user_id))
        
    def remove_member_from_project_repo(self, db: Session, ProjectMember: models.ProjectMember):
        db.delete(ProjectMember)
        db.commit()


