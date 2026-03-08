from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func, or_
from typing import Optional
from app.models.project import Project
from app.models.project_member import ProjectMember


class ProjectRepository:
    @staticmethod
    def get_by_id(db: Session, project_id: int) -> Optional[Project]:
        stmt = (
            select(Project)
            .where(Project.id == project_id)
            .options(selectinload(Project.members))
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def create(db: Session, **kwargs) -> Project:
        project = Project(**kwargs)
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def update(db: Session, project: Project, **kwargs) -> Project:
        for key, value in kwargs.items():
            setattr(project, key, value)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete(db: Session, project: Project) -> None:
        db.delete(project)
        db.commit()

    @staticmethod
    def list_for_user(
        db: Session,
        user_id: int,
        is_archived: Optional[bool] = False,
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Project], int]:
        accessible = (
            select(Project.id)
            .outerjoin(ProjectMember, ProjectMember.project_id == Project.id)
            .where(
                or_(
                    Project.owner_id == user_id,
                    ProjectMember.user_id == user_id,
                )
            )
        )
        stmt = select(Project).where(Project.id.in_(accessible))
        count_stmt = (
            select(func.count()).select_from(Project).where(Project.id.in_(accessible))
        )

        if is_archived is not None:
            stmt = stmt.where(Project.is_archived == is_archived)
            count_stmt = count_stmt.where(Project.is_archived == is_archived)
        if search:
            stmt = stmt.where(Project.name.ilike(f"%{search}%"))
            count_stmt = count_stmt.where(Project.name.ilike(f"%{search}%"))

        total = db.execute(count_stmt).scalar_one()
        projects = (
            db.execute(stmt.limit(limit).offset(offset).order_by(Project.id))
            .scalars()
            .all()
        )
        return list(projects), total

    @staticmethod
    def list_all(
        db: Session,
        is_archived: Optional[bool] = None,
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Project], int]:
        stmt = select(Project)
        count_stmt = select(func.count()).select_from(Project)

        if is_archived is not None:
            stmt = stmt.where(Project.is_archived == is_archived)
            count_stmt = count_stmt.where(Project.is_archived == is_archived)
        if search:
            stmt = stmt.where(Project.name.ilike(f"%{search}%"))
            count_stmt = count_stmt.where(Project.name.ilike(f"%{search}%"))

        total = db.execute(count_stmt).scalar_one()
        projects = (
            db.execute(stmt.limit(limit).offset(offset).order_by(Project.id))
            .scalars()
            .all()
        )
        return list(projects), total

    @staticmethod
    def get_member(
        db: Session, project_id: int, user_id: int
    ) -> Optional[ProjectMember]:
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def add_member(db: Session, project_id: int, user_id: int) -> ProjectMember:
        member = ProjectMember(project_id=project_id, user_id=user_id)
        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def remove_member(db: Session, member: ProjectMember) -> None:
        db.delete(member)
        db.commit()

    @staticmethod
    def list_members(db: Session, project_id: int) -> list[ProjectMember]:
        stmt = (
            select(ProjectMember)
            .where(ProjectMember.project_id == project_id)
            .options(selectinload(ProjectMember.user))
        )
        return list(db.execute(stmt).scalars().all())
