from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, case, func
from app import models
from datetime import date


class TaskRepository:

    def count_tasks(self, db: Session, project_id: int) -> int:
        stmt = select(func.count()).where(models.Task.project_id == project_id)
        return db.execute(stmt).scalar_one()

    def create(self, db: Session, task: models.Task) -> models.Task:
        db.add(task)
        return task

    def get_by_id(self, db: Session, task_id: int) -> models.Task | None:
        return db.get(models.Task, task_id)

    def list_tasks(
        self,
        db: Session,
        project_id: int,
        limit: int = 20,
        offset: int = 0,
        status: str | None = None,
        priority: str | None = None,
        assignee_id: int | None = None,
        due_date_from: date | None = None,
        due_date_to: date | None = None,
        q: str | None = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> list[models.Task]:

        stmt = select(models.Task).where(models.Task.project_id == project_id)

        if status:
            stmt = stmt.where(models.Task.status == status)

        if priority:
            stmt = stmt.where(models.Task.priority == priority)

        if due_date_from:
            stmt = stmt.where(models.Task.due_date >= due_date_from)

        if due_date_to:
            stmt = stmt.where(models.Task.due_date <= due_date_to)

        if q:
            stmt = stmt.where(
                or_(
                    models.Task.title.ilike(f"%{q}%"),
                    models.Task.description.ilike(f"%{q}%"),
                )
            )

        if assignee_id:
            stmt = stmt.join(models.TaskAssignment).where(
                models.TaskAssignment.user_id == assignee_id
            )

        if sort_by == "priority":
            priority_order = case(
                (models.Task.priority == "high", 3),
                (models.Task.priority == "medium", 2),
                (models.Task.priority == "low", 1),
            )

            if sort_dir == "desc":
                stmt = stmt.order_by(priority_order.desc())
            else:
                stmt = stmt.order_by(priority_order.asc())

        else:
            sort_column = getattr(models.Task, sort_by)

            if sort_dir == "desc":
                stmt = stmt.order_by(sort_column.desc())
            else:
                stmt = stmt.order_by(sort_column.asc())

        stmt = stmt.limit(limit).offset(offset)

        return db.execute(stmt).scalars().all()

    def update(
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

        return task

    def change_due_date(
        self, db: Session, task: models.Task, due_date: date | None = None
    ) -> models.Task:
        if due_date is not None:
            task.due_date = due_date
        return task

    def delete(self, db: Session, task: models.Task) -> None:
        db.delete(task)
