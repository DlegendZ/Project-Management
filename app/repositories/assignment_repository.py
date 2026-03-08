from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from typing import Optional
from app.models.assignment import Assignment


class AssignmentRepository:
    @staticmethod
    def get_by_task_and_user(
        db: Session, task_id: int, user_id: int
    ) -> Optional[Assignment]:
        stmt = select(Assignment).where(
            Assignment.task_id == task_id,
            Assignment.user_id == user_id,
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def create(db: Session, task_id: int, user_id: int, assigned_by: int) -> Assignment:
        assignment = Assignment(
            task_id=task_id, user_id=user_id, assigned_by=assigned_by
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        # reload with relationships
        return db.execute(
            select(Assignment)
            .where(Assignment.id == assignment.id)
            .options(selectinload(Assignment.assignee))
        ).scalar_one()

    @staticmethod
    def delete(db: Session, assignment: Assignment) -> None:
        db.delete(assignment)
        db.commit()

    @staticmethod
    def list_for_task(db: Session, task_id: int) -> list[Assignment]:
        stmt = (
            select(Assignment)
            .where(Assignment.task_id == task_id)
            .options(selectinload(Assignment.assignee))
        )
        return list(db.execute(stmt).scalars().all())
