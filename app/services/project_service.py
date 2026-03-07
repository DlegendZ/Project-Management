from sqlalchemy.orm import Session
from app.repositories.project_repository import ProjectRepository
from app import models
from app.exceptions.errors import ResourceNotFoundError, PermissionDeniedError


class ProjectService:

    def __init__(self):
        self.repo = ProjectRepository()

    def ensure_found(self, resource):
        if not resource:
            raise ResourceNotFoundError("project_not_found")
        return resource

    def ensure_owner_or_admin(self, user: models.User, project: models.Project):
        if user.role != "admin" and project.owner_id != user.id:
            raise PermissionDeniedError("permission_denied")

    def create_project(self, db: Session, project: models.Project):
        project = self.repo.create(db, project)
        db.commit()
        db.refresh(project)
        return project

    def list_projects(self, db: Session, limit: int = 20, offset: int = 0):
        projects = self.repo.list_projects(db, limit, offset)
        total = self.repo.count_projects(db)

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": projects,
        }

    def update_project(
        self,
        db: Session,
        user: models.User,
        project: models.Project,
        name=None,
        description=None,
    ):
        project = self.ensure_found(project)
        self.ensure_owner_or_admin(user, project)

        project = self.repo.update(db, project, name, description)
        db.commit()
        db.refresh(project)
        return project

    def archive_project(self, db: Session, user: models.User, project: models.Project):
        project = self.ensure_found(project)
        self.ensure_owner_or_admin(user, project)

        project = self.repo.archive(db, project)
        db.commit()
        db.refresh(project)
        return project

    def delete_project(self, db: Session, user: models.User, project: models.Project):
        project = self.ensure_found(project)
        self.ensure_owner_or_admin(user, project)

        self.repo.delete(db, project)
        db.commit()

    def add_member(
        self,
        db: Session,
        user: models.User,
        project: models.Project,
        project_member: models.ProjectMember,
    ):
        project = self.ensure_found(project)
        self.ensure_owner_or_admin(user, project)

        member = self.repo.add_member(db, project_member)
        db.commit()
        db.refresh(member)
        return member

    def remove_member(
        self,
        db: Session,
        user: models.User,
        project: models.Project,
        project_member: models.ProjectMember,
    ):
        project = self.ensure_found(project)
        self.ensure_owner_or_admin(user, project)

        self.repo.remove_member(db, project_member)
        db.commit()
