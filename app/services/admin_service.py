from app.repositories.admin_repository import AdminRepository
from app import models
from app.utils import ensure_found, normalize_limit, normalize_offset
from datetime import date


class AdminService:

    # ------------------------
    # User Management
    # ------------------------

    def __init__(self):
        self.repo = AdminRepository()

    def get_user_by_id_service(self, db, user_id: int) -> models.User:
        user = self.repo.get_user_by_id_repo(db, user_id)
        ensure_found(user)
        return user

    def list_users_service(
        self, db, limit: int | None = None, offset: int | None = None
    ) -> list[models.User]:
        limit = normalize_limit(limit)
        offset = normalize_offset(offset)
        return self.repo.list_users_repo(db, limit, offset)

    def deactivate_user_service(self, db, user_id: int) -> models.User:
        user = self.get_user_by_id_service(db, user_id)
        ensure_found(user)
        return self.repo.deactivate_user_repo(db, user)

    def delete_user_service(self, db, user_id: int) -> None:
        user = self.get_user_by_id_service(db, user_id)
        ensure_found(user)
        return self.repo.delete_user_repo(db, user)

    def update_user_profile_service(
        self,
        db,
        user_id: int,
        username: str | None = None,
        email: str | None = None,
        hashed_password: str | None = None,
    ) -> models.User:
        user = self.repo.get_user_by_id_repo(db, user_id)
        ensure_found(user)
        return self.repo.update_user_profile_repo(
            db, user, username, email, hashed_password
        )

    # ------------------------
    # Project Management
    # ------------------------

    def create_project_service(
        self, db, name: str, description: str | None = None
    ) -> models.Project:
        project = models.Project(name=name, description=description)
        return self.repo.create_project_repo(db, project)

    def get_project_by_id_service(self, db, project_id: int) -> models.Project:
        project = self.repo.get_project_by_id_repo(db, project_id)
        ensure_found(project)
        return project

    def list_projects_service(
        self, db, limit: int | None = None, offset: int | None = None
    ) -> list[models.Project]:
        limit = normalize_limit(limit)
        offset = normalize_offset(offset)
        return self.repo.list_projects_repo(db, limit, offset)

    def update_project_service(
        self,
        db,
        project_id: int,
        name: str | None = None,
        description: str | None = None,
    ) -> models.Project:
        project = self.repo.get_project_by_id_repo(db, project_id)
        ensure_found(project)
        return self.repo.update_project_repo(db, project, name, description)

    def archive_project_service(self, db, project_id: int) -> models.Project:
        project = self.repo.get_project_by_id_repo(db, project_id)
        ensure_found(project)
        return self.repo.archive_project_repo(db, project)

    def delete_project_service(self, db, project_id: int) -> None:
        project = self.repo.get_project_by_id_repo(db, project_id)
        ensure_found(project)
        return self.repo.delete_project_repo(db, project)

    def add_member_to_project_service(
        self, db, project_id: int, user_id: int
    ) -> models.ProjectMember:
        project = self.repo.get_project_by_id_repo(db, project_id)
        ensure_found(project)
        user = self.repo.get_user_by_id_repo(db, user_id)
        ensure_found(user)

        project_member = models.ProjectMember(project_id=project.id, user_id=user.id)

        return self.repo.add_member_to_project_repo(db, project_member)

    def get_project_member_by_id_service(
        self, db, user_id: int, project_id: int
    ) -> models.ProjectMember:
        project_member = self.repo.get_project_member_by_id_repo(
            db, user_id, project_id
        )
        ensure_found(project_member)
        return project_member

    def remove_member_from_project_service(
        self, db, user_id: int, project_id: int
    ) -> None:
        project_member = self.repo.get_project_member_by_id_repo(
            db, user_id, project_id
        )
        ensure_found(project_member)
        return self.repo.remove_member_from_project_repo(db, project_member)

    # ------------------------
    # Task Management
    # ------------------------

    def create_task_service(
        self,
        db,
        project_id: int,
        title: str,
        description: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        due_date: date | None = None,
    ) -> models.Task:
        project = self.repo.get_project_by_id_repo(db, project_id)
        ensure_found(project)

        task = models.Task(
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
            project_id=project.id,
        )
        return self.repo.create_task_repo(db, task)

    def get_task_by_id_service(self, db, task_id: int) -> models.Task:
        task = self.repo.get_task_by_id_repo(db, task_id)
        ensure_found(task)
        return task

    def list_tasks_service(
        self, db, project_id: int, limit: int | None = None, offset: int | None = None
    ) -> list[models.Task]:
        limit = normalize_limit(limit)
        offset = normalize_offset(offset)
        return self.repo.list_tasks_repo(db, project_id, limit, offset)

    def update_task_service(
        self,
        db,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
        priority: str | None = None,
    ) -> models.Task:
        task = self.repo.get_task_by_id_repo(db, task_id)
        ensure_found(task)
        return self.repo.update_task_repo(
            db, task, title, description, status, priority
        )

    def delete_task_service(self, db, task_id: int) -> None:
        task = self.repo.get_task_by_id_repo(db, task_id)
        ensure_found(task)
        return self.repo.delete_task_repo(db, task)

    def change_task_due_date_service(
        self, db, task_id: int, due_date: date | None = None
    ) -> models.Task:
        task = self.repo.get_task_by_id_repo(db, task_id)
        ensure_found(task)
        return self.repo.change_task_due_date_repo(db, task, due_date)

    # ------------------------
    # Assignment Management
    # ------------------------

    def assign_task_to_user_service(
        self, db, task_id: int, user_id: int, assigned_by: int
    ) -> models.TaskAssignment:
        task = self.repo.get_task_by_id_repo(db, task_id)
        ensure_found(task)
        user = self.repo.get_user_by_id_repo(db, user_id)
        ensure_found(user)
        assigner = self.repo.get_user_by_id_repo(db, assigned_by)
        ensure_found(assigner)

        assignment = models.TaskAssignment(
            task_id=task.id, user_id=user.id, assigned_by=assigner.id
        )
        return self.repo.assign_task_to_user_repo(db, assignment)

    def get_task_assignment_by_id_service(
        self, db, task_id: int, user_id: int
    ) -> models.TaskAssignment:
        assignment = self.repo.get_task_assignment_by_id_repo(db, task_id, user_id)
        ensure_found(assignment)
        return assignment

    def view_task_assignments_service(
        self, db, limit: int | None = None, offset: int | None = None
    ) -> list[models.TaskAssignment]:
        limit = normalize_limit(limit)
        offset = normalize_offset(offset)
        return self.repo.view_task_assignments_repo(db, limit, offset)

    def unassign_task_from_user_service(self, db, task_id: int, user_id: int) -> None:
        assignment = self.repo.get_task_assignment_by_id_repo(db, task_id, user_id)
        ensure_found(assignment)
        return self.repo.unassign_task_from_user_repo(db, assignment)

    def view_own_assignments_service(
        self, db, user_id: int, limit: int | None = None, offset: int | None = None
    ) -> list[models.TaskAssignment]:
        limit = normalize_limit(limit)
        offset = normalize_offset(offset)
        return self.repo.view_own_assignments_repo(db, user_id, limit, offset)
