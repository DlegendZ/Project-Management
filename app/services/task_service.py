from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.models.user import User, UserRole
from app.models.task import Task, TaskStatus, TaskPriority
from app.repositories.task_repository import TaskRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.assignment_repository import AssignmentRepository
from app.exceptions import NotFoundException, ForbiddenException, BadRequestException
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    @staticmethod
    def _get_project_and_check_membership(db: Session, project_id: int, user: User):
        from app.services.project_service import ProjectService

        return ProjectService._get_accessible_project(db, project_id, user)

    @staticmethod
    def create_task(db: Session, project_id: int, user: User, data: TaskCreate) -> Task:
        TaskService._get_project_and_check_membership(db, project_id, user)
        if data.due_date and data.due_date < date.today():
            raise BadRequestException("due_date must not be in the past")

        task = TaskRepository.create(
            db,
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
            due_date=data.due_date,
            project_id=project_id,
            created_by=user.id,
        )

        # Create assignments if provided
        if data.assignee_ids:
            for assignee_id in data.assignee_ids:
                AssignmentRepository.create(db, task.id, assignee_id, user.id)
            # Refresh task to include assignments
            task = TaskRepository.get_by_id(db, task.id)

        return task

    @staticmethod
    def get_task(db: Session, project_id: int, task_id: int, user: User) -> Task:
        TaskService._get_project_and_check_membership(db, project_id, user)
        task = TaskRepository.get_by_id(db, task_id)
        if not task or task.project_id != project_id:
            raise NotFoundException("Task not found")
        return task

    @staticmethod
    def list_tasks(
        db: Session,
        project_id: int,
        user: User,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        assignee_id: Optional[int] = None,
        due_date_from: Optional[date] = None,
        due_date_to: Optional[date] = None,
        is_overdue: Optional[bool] = None,
        created_by: Optional[int] = None,
        q: Optional[str] = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
        limit: int = 20,
        offset: int = 0,
    ):
        TaskService._get_project_and_check_membership(db, project_id, user)
        if due_date_from and due_date_to and due_date_from > due_date_to:
            raise BadRequestException("due_date_from must not be after due_date_to")
        return TaskRepository.list_for_project(
            db,
            project_id,
            status=status,
            priority=priority,
            assignee_id=assignee_id,
            due_date_from=due_date_from,
            due_date_to=due_date_to,
            is_overdue=is_overdue,
            created_by=created_by,
            q=q,
            sort_by=sort_by,
            sort_dir=sort_dir,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def update_task(
        db: Session, project_id: int, task_id: int, user: User, data: TaskUpdate
    ) -> Task:
        project = TaskService._get_project_and_check_membership(db, project_id, user)
        task = TaskRepository.get_by_id(db, task_id)
        if not task or task.project_id != project_id:
            raise NotFoundException("Task not found")

        is_owner = project.owner_id == user.id
        is_creator = task.created_by == user.id
        is_admin = user.role == UserRole.admin
        is_assignee = AssignmentRepository.get_by_task_and_user(db, task_id, user.id) is not None

        if is_admin or is_owner or is_creator or is_assignee:
            # Full update allowed
            updates = {k: v for k, v in data.model_dump(exclude_unset=True).items()}
        else:
            raise ForbiddenException(
                "permission_denied", "You don't have permission to update this task"
            )

        # Handle assignee_ids separately
        assignee_ids = updates.pop("assignee_ids", None)

        if updates:
            task = TaskRepository.update(db, task, **updates)

        # Update assignments if assignee_ids was provided
        if assignee_ids is not None:
            # Delete existing assignments
            existing_assignments = AssignmentRepository.list_for_task(db, task_id)
            for assignment in existing_assignments:
                AssignmentRepository.delete(db, assignment)

            # Create new assignments
            for user_id in assignee_ids:
                AssignmentRepository.create(db, task_id, user_id, user.id)

        return task

    @staticmethod
    def delete_task(db: Session, project_id: int, task_id: int, user: User) -> None:
        project = TaskService._get_project_and_check_membership(db, project_id, user)
        task = TaskRepository.get_by_id(db, task_id)
        if not task or task.project_id != project_id:
            raise NotFoundException("Task not found")

        is_owner = project.owner_id == user.id
        is_creator = task.created_by == user.id
        is_admin = user.role == UserRole.admin

        if not (is_admin or is_owner or is_creator):
            raise ForbiddenException(
                "permission_denied",
                "Only project owners or task creators can delete tasks",
            )
        TaskRepository.delete(db, task)

    @staticmethod
    def list_my_tasks(
        db: Session,
        user: User,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
        limit: int = 20,
        offset: int = 0,
    ):
        return TaskRepository.list_assigned_to_user(
            db,
            user.id,
            status=status,
            priority=priority,
            sort_by=sort_by,
            sort_dir=sort_dir,
            limit=limit,
            offset=offset,
        )
