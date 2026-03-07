from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func, case, or_
from typing import Optional
from datetime import date
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.assignment import Assignment


PRIORITY_ORDER = case(
    (Task.priority == TaskPriority.high, 1),
    (Task.priority == TaskPriority.medium, 2),
    (Task.priority == TaskPriority.low, 3),
    else_=4,
)


class TaskRepository:
    @staticmethod
    def get_by_id(db: Session, task_id: int) -> Optional[Task]:
        stmt = (
            select(Task)
            .where(Task.id == task_id)
            .options(selectinload(Task.assignments).selectinload(Assignment.assignee))
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def create(db: Session, **kwargs) -> Task:
        task = Task(**kwargs)
        db.add(task)
        db.commit()
        db.refresh(task)
        return db.execute(
            select(Task)
            .where(Task.id == task.id)
            .options(selectinload(Task.assignments).selectinload(Assignment.assignee))
        ).scalar_one()

    @staticmethod
    def update(db: Session, task: Task, **kwargs) -> Task:
        for key, value in kwargs.items():
            setattr(task, key, value)
        db.commit()
        return db.execute(
            select(Task)
            .where(Task.id == task.id)
            .options(selectinload(Task.assignments).selectinload(Assignment.assignee))
        ).scalar_one()

    @staticmethod
    def delete(db: Session, task: Task) -> None:
        db.delete(task)
        db.commit()

    @staticmethod
    def list_for_project(
        db: Session,
        project_id: int,
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
    ) -> tuple[list[Task], int]:
        stmt = select(Task).where(Task.project_id == project_id)
        count_stmt = select(func.count()).select_from(Task).where(Task.project_id == project_id)

        if status:
            stmt = stmt.where(Task.status == status)
            count_stmt = count_stmt.where(Task.status == status)
        if priority:
            stmt = stmt.where(Task.priority == priority)
            count_stmt = count_stmt.where(Task.priority == priority)
        if assignee_id:
            sub = select(Assignment.task_id).where(Assignment.user_id == assignee_id)
            stmt = stmt.where(Task.id.in_(sub))
            count_stmt = count_stmt.where(Task.id.in_(sub))
        if due_date_from:
            stmt = stmt.where(Task.due_date >= due_date_from)
            count_stmt = count_stmt.where(Task.due_date >= due_date_from)
        if due_date_to:
            stmt = stmt.where(Task.due_date <= due_date_to)
            count_stmt = count_stmt.where(Task.due_date <= due_date_to)
        if is_overdue is True:
            today = date.today()
            stmt = stmt.where(Task.due_date < today, Task.status != TaskStatus.done)
            count_stmt = count_stmt.where(Task.due_date < today, Task.status != TaskStatus.done)
        if created_by:
            stmt = stmt.where(Task.created_by == created_by)
            count_stmt = count_stmt.where(Task.created_by == created_by)
        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(or_(Task.title.ilike(pattern), Task.description.ilike(pattern)))
            count_stmt = count_stmt.where(or_(Task.title.ilike(pattern), Task.description.ilike(pattern)))

        # Sort
        sort_col_map = {
            "created_at": Task.created_at,
            "updated_at": Task.updated_at,
            "due_date": Task.due_date,
            "priority": PRIORITY_ORDER,
        }
        sort_col = sort_col_map.get(sort_by, Task.created_at)
        if sort_by == "priority":
            order_expr = sort_col if sort_dir == "asc" else sort_col.desc()
        else:
            order_expr = sort_col.asc() if sort_dir == "asc" else sort_col.desc()

        total = db.execute(count_stmt).scalar_one()
        tasks = db.execute(
            stmt.options(selectinload(Task.assignments).selectinload(Assignment.assignee))
            .order_by(order_expr)
            .limit(limit)
            .offset(offset)
        ).scalars().all()
        return list(tasks), total

    @staticmethod
    def list_assigned_to_user(
        db: Session, user_id: int, limit: int = 20, offset: int = 0
    ) -> tuple[list[Task], int]:
        sub = select(Assignment.task_id).where(Assignment.user_id == user_id)
        stmt = select(Task).where(Task.id.in_(sub))
        count_stmt = select(func.count()).select_from(Task).where(Task.id.in_(sub))

        total = db.execute(count_stmt).scalar_one()
        tasks = db.execute(
            stmt.options(selectinload(Task.assignments).selectinload(Assignment.assignee))
            .limit(limit).offset(offset).order_by(Task.created_at.desc())
        ).scalars().all()
        return list(tasks), total
