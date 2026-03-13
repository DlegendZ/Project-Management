from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User, UserRole
from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository
from app.exceptions import NotFoundException, ForbiddenException, ConflictException
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    @staticmethod
    def _get_accessible_project(db: Session, project_id: int, user: User) -> Project:
        project = ProjectRepository.get_by_id(db, project_id)
        if not project:
            raise NotFoundException("Project not found")
        if user.role == UserRole.admin:
            return project
        is_owner = project.owner_id == user.id
        is_member = ProjectRepository.get_member(db, project_id, user.id) is not None
        if not is_owner and not is_member:
            raise NotFoundException("Project not found")
        return project

    @staticmethod
    def _require_owner_or_admin(project: Project, user: User):
        if user.role != UserRole.admin and project.owner_id != user.id:
            raise ForbiddenException(
                "permission_denied", "Only the project owner can perform this action"
            )

    @staticmethod
    def create_project(db: Session, user: User, data: ProjectCreate) -> Project:
        project = ProjectRepository.create(
            db, name=data.name, description=data.description, owner_id=user.id
        )
        # Auto-add owner as member
        ProjectRepository.add_member(db, project.id, user.id)
        return project

    @staticmethod
    def list_projects(
        db: Session,
        user: User,
        is_archived: Optional[bool] = False,
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ):
        if user.role == UserRole.admin:
            return ProjectRepository.list_all(
                db, is_archived=is_archived, search=search, limit=limit, offset=offset
            )
        return ProjectRepository.list_for_user(
            db,
            user.id,
            is_archived=is_archived,
            search=search,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def get_project(db: Session, project_id: int, user: User) -> Project:
        return ProjectService._get_accessible_project(db, project_id, user)

    @staticmethod
    def update_project(
        db: Session, project_id: int, user: User, data: ProjectUpdate
    ) -> Project:
        project = ProjectService._get_accessible_project(db, project_id, user)
        ProjectService._require_owner_or_admin(project, user)
        updates = {
            k: v
            for k, v in data.model_dump(exclude_unset=True).items()
            if v is not None
        }
        if updates:
            return ProjectRepository.update(db, project, **updates)
        return project

    @staticmethod
    def archive_project(db: Session, project_id: int, user: User) -> Project:
        project = ProjectService._get_accessible_project(db, project_id, user)
        ProjectService._require_owner_or_admin(project, user)
        return ProjectRepository.update(
            db, project, is_archived=not project.is_archived
        )

    @staticmethod
    def delete_project(db: Session, project_id: int, user: User) -> None:
        project = ProjectService._get_accessible_project(db, project_id, user)
        ProjectService._require_owner_or_admin(project, user)
        ProjectRepository.delete(db, project)

    @staticmethod
    def add_member(db: Session, project_id: int, user: User, member_user_id: int):
        project = ProjectService._get_accessible_project(db, project_id, user)
        ProjectService._require_owner_or_admin(project, user)
        target = UserRepository.get_by_id(db, member_user_id)
        if not target:
            raise NotFoundException("User not found")
        existing = ProjectRepository.get_member(db, project_id, member_user_id)
        if existing:
            raise ConflictException("conflict", "User is already a member")
        return ProjectRepository.add_member(db, project_id, member_user_id)

    @staticmethod
    def remove_member(
        db: Session, project_id: int, user: User, member_user_id: int
    ) -> None:
        project = ProjectService._get_accessible_project(db, project_id, user)
        ProjectService._require_owner_or_admin(project, user)
        member = ProjectRepository.get_member(db, project_id, member_user_id)
        if not member:
            raise NotFoundException("Member not found")
        ProjectRepository.remove_member(db, member)

    @staticmethod
    def list_members(db: Session, project_id: int, user: User):
        project = ProjectService._get_accessible_project(db, project_id, user)
        members = ProjectRepository.list_members(db, project_id)
        return [m.user for m in members]
