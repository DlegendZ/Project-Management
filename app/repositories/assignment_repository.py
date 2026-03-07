from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app import models


class AssignmentRepository:

    def count_assignments_for_task(self, db: Session, task_id: int) -> int:
        stmt = select(func.count()).where(models.TaskAssignment.task_id == task_id)
        return db.execute(stmt).scalar_one()

    def assign(
        self, db: Session, assignment: models.TaskAssignment
    ) -> models.TaskAssignment:
        db.add(assignment)
        return assignment

    def get(
        self, db: Session, task_id: int, user_id: int
    ) -> models.TaskAssignment | None:
        return db.get(models.TaskAssignment, (task_id, user_id))

    def list_for_task(
        self, db: Session, task_id: int, limit: int = 20, offset: int = 0
    ) -> list[models.TaskAssignment]:
        stmt = (
            select(models.TaskAssignment)
            .where(models.TaskAssignment.task_id == task_id)
            .limit(limit)
            .offset(offset)
        )
        return db.execute(stmt).scalars().all()

    def unassign(self, db: Session, assignment: models.TaskAssignment) -> None:
        db.delete(assignment)

    def list_tasks_for_user(
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
