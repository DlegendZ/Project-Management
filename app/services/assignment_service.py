from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.repositories.assignment_repository import AssignmentRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.exceptions import NotFoundException, ForbiddenException, ConflictException


class AssignmentService:
    @staticmethod
    def _check_owner_or_admin(project, user: User):
        if user.role != UserRole.admin and project.owner_id != user.id:
            raise ForbiddenException("permission_denied", "Only project owners can manage assignments")

    @staticmethod
    def assign_user(db: Session, project_id: int, task_id: int, user: User, assignee_id: int):
        from app.services.project_service import ProjectService
        project = ProjectService._get_accessible_project(db, project_id, user)
        AssignmentService._check_owner_or_admin(project, user)

        task = TaskRepository.get_by_id(db, task_id)
        if not task or task.project_id != project_id:
            raise NotFoundException("Task not found")

        # Assignee must be a project member
        member = ProjectRepository.get_member(db, project_id, assignee_id)
        if not member:
            raise ForbiddenException("not_a_member", "User must be a project member to be assigned")

        existing = AssignmentRepository.get_by_task_and_user(db, task_id, assignee_id)
        if existing:
            raise ConflictException("duplicate_assignment", "User already assigned to this task")

        return AssignmentRepository.create(db, task_id=task_id, user_id=assignee_id, assigned_by=user.id)

    @staticmethod
    def unassign_user(db: Session, project_id: int, task_id: int, user: User, assignee_id: int) -> None:
        from app.services.project_service import ProjectService
        project = ProjectService._get_accessible_project(db, project_id, user)
        AssignmentService._check_owner_or_admin(project, user)

        task = TaskRepository.get_by_id(db, task_id)
        if not task or task.project_id != project_id:
            raise NotFoundException("Task not found")

        assignment = AssignmentRepository.get_by_task_and_user(db, task_id, assignee_id)
        if not assignment:
            raise NotFoundException("Assignment not found")
        AssignmentRepository.delete(db, assignment)

    @staticmethod
    def list_assignments(db: Session, project_id: int, task_id: int, user: User):
        from app.services.project_service import ProjectService
        ProjectService._get_accessible_project(db, project_id, user)
        task = TaskRepository.get_by_id(db, task_id)
        if not task or task.project_id != project_id:
            raise NotFoundException("Task not found")
        return AssignmentRepository.list_for_task(db, task_id)
