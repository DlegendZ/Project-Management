from app.repositories.user_repository import UserRepository
from app import models
from app.utils.common import ensure_found, normalize_limit, normalize_offset
from datetime import date
from app.exceptions.errors import PermissionError


class AdminService:

    # ------------------------
    # User Management
    # ------------------------

    def __init__(self):
        self.repo = UserRepository()

    def get_user_by_id_service(self, db, user_id: int) -> models.User:
        user = self.repo.get_user_by_id_repo(db, user_id)
        ensure_found(user)
        return user

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

    def get_project_by_id_service(
        self, db, project_id: int, user_id: int
    ) -> models.Project:
        project = ensure_found(self.repo.get_project_by_id_repo(db, project_id))

        if project.owner_id == user_id:
            return project

        is_member = self.repo.get_project_member_by_id_repo(db, user_id, project_id)

        if not is_member:
            raise PermissionError("You do not have permission to access this project")

        return project

    def list_projects_service(
        self, db, user_id: int, limit: int | None = None, offset: int | None = None
    ) -> list[models.Project]:
        limit = normalize_limit(limit)
        offset = normalize_offset(offset)
        return self.repo.list_projects_owned_member_repo(db, user_id, limit, offset)

    def update_project_service(
        self,
        db,
        project_id: int,
        user_id: int,
        name: str | None = None,
        description: str | None = None,
    ) -> models.Project:
        project = self.repo.get_project_by_id_repo(db, project_id)
        ensure_found(project)

        is_owner = project.owner_id == user_id

        if not is_owner:
            raise PermissionError("Only the project owner can update the project")

        return self.repo.update_project_repo(db, project, name, description)

    def archive_project_service(
        self, db, project_id: int, user_id: int
    ) -> models.Project:
        project = self.repo.get_project_by_id_repo(db, project_id)
        ensure_found(project)

        is_owner = project.owner_id == user_id

        if not is_owner:
            raise PermissionError("Only the project owner can archive the project")

        return self.repo.archive_project_repo(db, project)

    def delete_project_service(self, db, project_id: int, user_id: int) -> None:
        project = self.repo.get_project_by_id_repo(db, project_id)
        ensure_found(project)

        is_owner = project.owner_id == user_id

        if not is_owner:
            raise PermissionError("Only the project owner can delete the project")

        return self.repo.delete_project_repo(db, project)

    def add_member_to_project_service(
        self, db, project_id: int, user_id: int, owner_id: int
    ) -> models.ProjectMember:
        project = self.repo.get_project_by_id_repo(db, project_id)
        ensure_found(project)

        is_owner = project.owner_id == owner_id

        if not is_owner:
            raise PermissionError(
                "Only the project owner can add members to the project"
            )

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
        self, db, user_id: int, project_id: int, owner_id: int
    ) -> None:
        project = self.repo.get_project_by_id_repo(db, project_id)
        ensure_found(project)

        is_owner = project.owner_id == owner_id

        if not is_owner:
            raise PermissionError(
                "Only the project owner can remove members from the project"
            )

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
        user_id: int,
        project_id: int,
        title: str,
        description: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        due_date: date | None = None,
    ) -> models.Task:
        project = ensure_found(self.repo.get_project_by_id_repo(db, project_id))

        if project.owner_id == user_id:
            pass
        else:
            is_member = self.repo.get_project_member_by_id_repo(db, user_id, project_id)
            if not is_member:
                raise PermissionError(
                    "You do not have permission to create tasks in this project"
                )

        task = models.Task(
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
            project_id=project.id,
        )
        return self.repo.create_task_repo(db, task)

    def get_task_by_id_service(
        self, db, task_id: int, project_id: int, user_id: int
    ) -> models.Task:
        task = ensure_found(self.repo.get_task_by_id_repo(db, task_id))

        if task.created_by == user_id:
            return task

        project = ensure_found(self.repo.get_project_by_id_repo(db, project_id))

        if project.owner_id == user_id:
            return task

        is_project_member = self.repo.get_project_member_by_id_repo(
            db, user_id, project_id
        )

        if not is_project_member:
            raise PermissionError("You do not have permission to access this task")

        return task

    def list_tasks_service(
        self,
        db,
        user_id: int,
        project_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[models.Task]:
        project = ensure_found(self.repo.get_project_by_id_repo(db, project_id))

        if project.owner_id == user_id:
            pass
        else:
            is_member = self.repo.get_project_member_by_id_repo(db, user_id, project_id)
            if not is_member:
                raise PermissionError(
                    "You do not have permission to view tasks in this project"
                )

        limit = normalize_limit(limit)
        offset = normalize_offset(offset)
        return self.repo.list_tasks_repo(db, project_id, limit, offset)

    def update_task_service(
        self,
        db,
        task_id: int,
        user_id: int,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
        priority: str | None = None,
    ) -> models.Task:
        task = ensure_found(self.repo.get_task_by_id_repo(db, task_id))

        if task.created_by == user_id:
            pass
        else:
            project = ensure_found(
                self.repo.get_project_by_id_repo(db, task.project_id)
            )
            if not project.owner_id == user_id:
                raise PermissionError("You do not have permission to update this task")

        return self.repo.update_task_repo(
            db, task, title, description, status, priority
        )

    def delete_task_service(self, db, task_id: int, user_id: int) -> None:
        task = ensure_found(self.repo.get_task_by_id_repo(db, task_id))

        if task.created_by == user_id:
            pass
        else:
            project = ensure_found(
                self.repo.get_project_by_id_repo(db, task.project_id)
            )
            if not project.owner_id == user_id:
                raise PermissionError("You do not have permission to delete this task")

        return self.repo.delete_task_repo(db, task)

    def change_task_due_date_service(
        self, db, task_id: int, user_id: int, due_date: date | None = None
    ) -> models.Task:
        task = ensure_found(self.repo.get_task_by_id_repo(db, task_id))

        if task.created_by == user_id:
            pass
        else:
            project = ensure_found(
                self.repo.get_project_by_id_repo(db, task.project_id)
            )
            if not project.owner_id == user_id:
                raise PermissionError(
                    "You do not have permission to change the due date of this task"
                )

        return self.repo.change_task_due_date_repo(db, task, due_date)

    # ------------------------
    # Assignment Management
    # ------------------------

    def assign_task_to_user_service(
        self,
        db,
        task_id: int,
        user_id: int,
        assigned_by: int,
    ) -> models.TaskAssignment:
        task = ensure_found(self.repo.get_task_by_id_repo(db, task_id))

        project = ensure_found(self.repo.get_project_by_id_repo(db, task.project_id))
        if not project.owner_id == assigned_by:
            raise PermissionError(
                "You do not have permission to assign tasks in this project"
            )

        user = ensure_found(self.repo.get_user_by_id_repo(db, user_id))
        assigner = ensure_found(self.repo.get_user_by_id_repo(db, assigned_by))

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
        self,
        db,
        project_id: int,
        user_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[models.TaskAssignment]:
        project = ensure_found(self.repo.get_project_by_id_repo(db, project_id))
        if project.owner_id == user_id:
            pass
        else:
            is_member = self.repo.get_project_member_by_id_repo(db, user_id, project_id)
            if not is_member:
                raise PermissionError(
                    "You do not have permission to view task assignments in this project"
                )

        limit = normalize_limit(limit)
        offset = normalize_offset(offset)
        return self.repo.view_task_assignments_repo(db, limit, offset)

    def unassign_task_from_user_service(
        self, db, task_id: int, user_id: int, project_id: int
    ) -> None:
        project = ensure_found(self.repo.get_project_by_id_repo(db, project_id))
        if not project.owner_id == user_id:
            raise PermissionError(
                "You do not have permission to unassign tasks in this project"
            )

        assignment = self.repo.get_task_assignment_by_id_repo(db, task_id, user_id)
        ensure_found(assignment)
        return self.repo.unassign_task_from_user_repo(db, assignment)

    def view_own_assignments_service(
        self,
        db,
        user_id: int,
        project_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[models.TaskAssignment]:
        project = ensure_found(self.repo.get_project_by_id_repo(db, project_id))
        if project.owner_id == user_id:
            pass
        else:
            is_member = self.repo.get_project_member_by_id_repo(db, user_id, project_id)
            if not is_member:
                raise PermissionError(
                    "You do not have permission to view task assignments in this project"
                )

        limit = normalize_limit(limit)
        offset = normalize_offset(offset)
        return self.repo.view_own_assignments_repo(db, user_id, limit, offset)
