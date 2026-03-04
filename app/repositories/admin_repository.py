from sqlalchemy.orm import Session
from sqlalchemy import select
from app import models
from datetime import date


class AdminRepository:

    # ------------------------
    # User Management
    # ------------------------

    def get_user_by_id_repo(self, db: Session, user_id: int) -> models.User | None:
        return db.get(models.User, user_id)

    def list_users_repo(
        self, db: Session, limit: int = 20, offset: int = 0
    ) -> list[models.User]:
        stmt = select(models.User).limit(limit).offset(offset)
        return db.execute(stmt).scalars().all()

    # def create_user(self, db: Session, user: models.User):
    #     db.add(user)
    #     db.commit()
    #     db.refresh(user)
    #     return user

    def deactivate_user_repo(self, db: Session, user: models.User) -> models.User:
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user

    def delete_user_repo(self, db: Session, user: models.User) -> None:
        db.delete(user)
        db.commit()

    def update_user_profile_repo(
        self,
        db: Session,
        user: models.User,
        username: str | None = None,
        email: str | None = None,
        hashed_password: str | None = None,
    ) -> models.User:
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

    def create_project_repo(
        self, db: Session, project: models.Project
    ) -> models.Project:
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    def get_project_by_id_repo(
        self, db: Session, project_id: int
    ) -> models.Project | None:
        return db.get(models.Project, project_id)

    def list_projects_repo(
        self, db: Session, limit: int = 20, offset: int = 0
    ) -> list[models.Project]:
        stmt = select(models.Project).limit(limit).offset(offset)
        return db.execute(stmt).scalars().all()

    def update_project_repo(
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

        db.commit()
        db.refresh(project)
        return project

    def archive_project_repo(
        self, db: Session, project: models.Project
    ) -> models.Project:
        project.is_archived = True
        db.commit()
        db.refresh(project)
        return project

    def delete_project_repo(self, db: Session, project: models.Project) -> None:
        db.delete(project)
        db.commit()

    def add_member_to_project_repo(
        self, db: Session, ProjectMember: models.ProjectMember
    ) -> models.ProjectMember:
        db.add(ProjectMember)
        db.commit()
        db.refresh(ProjectMember)
        return ProjectMember

    def get_project_member_by_id_repo(
        self, db: Session, user_id: int, project_id: int
    ) -> models.ProjectMember | None:
        return db.get(models.ProjectMember, (project_id, user_id))

    def remove_member_from_project_repo(
        self, db: Session, ProjectMember: models.ProjectMember
    ) -> None:
        db.delete(ProjectMember)
        db.commit()

    # ------------------------
    # Task Management
    # ------------------------

    def create_task_repo(self, db: Session, task: models.Task) -> models.Task:
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def get_task_by_id_repo(self, db: Session, task_id: int) -> models.Task | None:
        return db.get(models.Task, task_id)

    def list_tasks_repo(
        self, db: Session, limit: int = 20, offset: int = 0
    ) -> list[models.Task]:
        stmt = select(models.Task).limit(limit).offset(offset)
        return db.execute(stmt).scalars().all()

    def update_task_repo(
        self,
        db: Session,
        task: models.Task,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
        priority: str | None = None,
    ) -> models.Task:
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.status = status
        if priority is not None:
            task.priority = priority

        db.commit()
        db.refresh(task)
        return task

    def delete_task_repo(self, db: Session, task: models.Task) -> None:
        db.delete(task)
        db.commit()

    def change_task_due_date(
        self, db: Session, task: models.Task, due_date: date | None = None
    ) -> models.Task:
        if due_date is not None:
            task.due_date = due_date
        db.commit()
        db.refresh(task)
        return task

    # ------------------------
    # Assignment Management
    # ------------------------

    def assign_task_to_user_repo(
        self, db: Session, task_assignment: models.TaskAssignment
    ) -> models.TaskAssignment:
        db.add(task_assignment)
        db.commit()
        db.refresh(task_assignment)
        return task_assignment

    def get_task_assignment_by_id_repo(
        self, db: Session, task_id: int, user_id: int
    ) -> models.TaskAssignment | None:
        return db.get(models.TaskAssignment, (task_id, user_id))

    def view_task_assignments_repo(
        self, db: Session, limit: int = 20, offset: int = 0
    ) -> list[models.TaskAssignment]:
        stmt = select(models.TaskAssignment).limit(limit).offset(offset)
        return db.execute(stmt).scalars().all()

    def unassign_task_from_user_repo(
        self, db: Session, task_assignment: models.TaskAssignment
    ) -> None:
        db.delete(task_assignment)
        db.commit()

    def view_own_assignments_repo(
        self, db: Session, user_id: int, limit: int = 20, offset: int = 0
    ) -> list[models.Task]:
        stmt = (
            select(models.Task)
            .join(
                models.TaskAssignment, models.Task.id == models.TaskAssignment.task_id
            )
            .where(models.TaskAssignment.user_id == user_id)
            .limit(limit)
            .offset(offset)
        )
        return db.execute(stmt).scalars().all()
