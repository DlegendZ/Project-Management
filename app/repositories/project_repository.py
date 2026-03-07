from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app import models


class ProjectRepository:

    def create(self, db: Session, project: models.Project) -> models.Project:
        db.add(project)
        return project

    def get_by_id(self, db: Session, project_id: int) -> models.Project | None:
        return db.get(models.Project, project_id)

    def list_projects(
        self, db: Session, limit: int = 20, offset: int = 0
    ) -> list[models.Project]:
        stmt = select(models.Project).limit(limit).offset(offset)
        return db.execute(stmt).scalars().all()

    def count_projects(self, db: Session) -> int:
        stmt = select(func.count()).select_from(models.Project)
        return db.execute(stmt).scalar_one()

    def update(
        self,
        db: Session,
        project: models.Project,
        name: str | None = None,
        description: str | None = None,
    ) -> models.Project:
        if name is not None:
            project.name = name
        if description is not None:
            project.description = description

        return project

    def archive(self, db: Session, project: models.Project) -> models.Project:
        project.is_archived = True
        return project

    def delete(self, db: Session, project: models.Project) -> None:
        db.delete(project)

    def add_member(
        self, db: Session, project_member: models.ProjectMember
    ) -> models.ProjectMember:
        db.add(project_member)
        return project_member

    def get_member(
        self, db: Session, user_id: int, project_id: int
    ) -> models.ProjectMember | None:
        return db.get(models.ProjectMember, (project_id, user_id))

    def remove_member(self, db: Session, project_member: models.ProjectMember) -> None:
        db.delete(project_member)
