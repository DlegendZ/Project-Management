from sqlalchemy.orm import Session
from app.repositories.assignment_repository import AssignmentRepository
from app import models
from app.exceptions.errors import ResourceNotFoundError, DuplicateAssignmentError


class AssignmentService:

    def __init__(self):
        self.repo = AssignmentRepository()

    def ensure_found(self, resource):
        if not resource:
            raise ResourceNotFoundError("assignment_not_found")
        return resource

    def assign_user(self, db: Session, assignment: models.TaskAssignment):
        existing = self.repo.get(db, assignment.task_id, assignment.user_id)

        if existing:
            raise DuplicateAssignmentError("duplicate_assignment")

        assignment = self.repo.assign(db, assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    def list_assignments(
        self, db: Session, task_id: int, limit: int = 20, offset: int = 0
    ):
        assignments = self.repo.list_for_task(db, task_id, limit, offset)
        total = self.repo.count_assignments_for_task(db, task_id)

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": assignments,
        }

    def unassign_user(self, db: Session, assignment: models.TaskAssignment):
        assignment = self.ensure_found(assignment)

        self.repo.unassign(db, assignment)
        db.commit()

    def list_tasks_for_user(
        self, db: Session, user_id: int, limit: int = 20, offset: int = 0
    ):
        return self.repo.list_tasks_for_user(db, user_id, limit, offset)
