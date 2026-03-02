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
        hashed_password: str | None = None
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

    def get_project_by_id_repo(self, db: Session, project_id: int):
        return db.get(models.Project, project_id)

    def list_projects_repo(
        self,
        db: Session,
        limit: int = 20,
        offset: int = 0
    ):
        stmt = select(models.Project).limit(limit).offset(offset)
        return db.execute(stmt).scalars().all()

    def create_project_repo(self, db: Session, project: models.Project):
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    def update_project_repo(
        self,
        db: Session,
        project: models.Project,
        name: str | None = None,
        description: str | None = None
    ):
        if name is not None:
            project.name = name
        if description is not None:
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

    def add_project_member_repo(
        self,
        db: Session,
        member: models.ProjectMember
    ):
        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    def remove_project_member_repo(
        self,
        db: Session,
        member: models.ProjectMember
    ):
        db.delete(member)
        db.commit()

    # ------------------------
    # Task Management
    # ------------------------

    def get_task_by_id_repo(
            self,
            db: Session,
            task_id: int
    ):
        return db.get(models.Task, task_id)

    def list_tasks_by_project_repo(
            self,
            db: Session,
            project_id: int,
            limit: int = 20,
            offset: int = 0
    ):
        stmt = (
            select(models.Task)
            .where(models.Task.project_id == project_id)
            .limit(limit)
            .offset(offset)
        )

        return db.execute(stmt).scalars().all()

    def create_task_repo(
            self,
            db: Session,
            task: models.Task
    ):
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def update_task_repo(
            self,
            db: Session,
            task: models.Task,
            title: str | None = None,
            description: str | None = None,
            status: str | None = None,
            priority: str | None = None,
            due_date=None
    ):
        if title is not None:
            task.title = title

        if description is not None:
            task.description = description

        if status is not None:
            task.status = status

        if priority is not None:
            task.priority = priority

        if due_date is not None:
            task.due_date = due_date

        db.commit()
        db.refresh(task)
        return task

    def delete_task_repo(
            self,
            db: Session,
            task: models.Task
    ):
        db.delete(task)
        db.commit()

        # ------------------------
        # Assignment Management
        # ------------------------

    def get_assignment_repo(
            self,
            db: Session,
            task_id: int,
            user_id: int
    ):
        stmt = select(models.TaskAssignment).where(
            and_(
                models.TaskAssignment.task_id == task_id,
                models.TaskAssignment.user_id == user_id
            )
        )
        return db.execute(stmt).scalars().first()

    def list_task_assignments_repo(
            self,
            db: Session,
            task_id: int
    ):
        stmt = select(models.TaskAssignment).where(
            models.TaskAssignment.task_id == task_id
        )
        return db.execute(stmt).scalars().all()

    def list_user_assignments_repo(
            self,
            db: Session,
            user_id: int,
            limit: int = 20,
            offset: int = 0
    ):
        stmt = (
            select(models.TaskAssignment)
            .where(models.TaskAssignment.user_id == user_id)
            .limit(limit)
            .offset(offset)
        )
        return db.execute(stmt).scalars().all()

    def create_assignment_repo(
            self,
            db: Session,
            assignment: models.TaskAssignment
    ):
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    def delete_assignment_repo(
            self,
            db: Session,
            assignment: models.TaskAssignment
    ):
        db.delete(assignment)
        db.commit()