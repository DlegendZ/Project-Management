from sqlalchemy.orm import Session
from app.repositories.task_repository import TaskRepository
from app import models
from app.exceptions.errors import ResourceNotFoundError, PermissionDeniedError


class TaskService:

    def __init__(self):
        self.repo = TaskRepository()

    def ensure_found(self, resource):
        if not resource:
            raise ResourceNotFoundError("task_not_found")
        return resource

    def ensure_owner_or_creator_or_admin(
        self, user: models.User, task: models.Task, project: models.Project
    ):
        if user.role == "admin":
            return

        if project.owner_id == user.id:
            return

        if task.created_by == user.id:
            return

        raise PermissionDeniedError("permission_denied")

    def create_task(self, db: Session, task: models.Task):
        task = self.repo.create(db, task)
        db.commit()
        db.refresh(task)
        return task

    def list_tasks(self, db: Session, project_id: int, **filters):
        tasks = self.repo.list_tasks(db, project_id, **filters)
        total = self.repo.count_tasks(db, project_id)

        return {
            "total": total,
            "limit": filters.get("limit", 20),
            "offset": filters.get("offset", 0),
            "items": tasks,
        }

    def update_task(
        self,
        db: Session,
        user: models.User,
        task: models.Task,
        project: models.Project,
        **fields
    ):
        task = self.ensure_found(task)
        self.ensure_owner_or_creator_or_admin(user, task, project)

        task = self.repo.update(db, task, **fields)
        db.commit()
        db.refresh(task)
        return task

    def change_due_date(
        self,
        db: Session,
        user: models.User,
        task: models.Task,
        project: models.Project,
        due_date,
    ):
        task = self.ensure_found(task)
        self.ensure_owner_or_creator_or_admin(user, task, project)

        task = self.repo.change_due_date(db, task, due_date)
        db.commit()
        db.refresh(task)
        return task

    def delete_task(
        self, db: Session, user: models.User, task: models.Task, project: models.Project
    ):
        task = self.ensure_found(task)
        self.ensure_owner_or_creator_or_admin(user, task, project)

        self.repo.delete(db, task)
        db.commit()
