from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.project_service import ProjectService
from app.database import get_db
from app.dependencies import get_current_user
from app import models

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])
service = ProjectService()


@router.get("")
def list_projects(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return service.list_projects(db, limit, offset)


@router.get("/{project_id}")
def get_project(
    project_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    project = service.repo.get_by_id(db, project_id)
    return project


@router.get("/{project_id}/members")
def list_members(
    project_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    project = service.repo.get_by_id(db, project_id)
    members = service.repo.list_members(db, project_id)
    return members


@router.post("")
def create_project(
    payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    project = models.Project(**payload, owner_id=user.id)
    return service.create_project(db, project)


@router.post("/{project_id}/members")
def add_member(
    project_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    project = service.repo.get_by_id(db, project_id)

    member = models.ProjectMember(project_id=project_id, user_id=payload.get("user_id"))

    return service.add_member(db, user, project, member)


@router.patch("/{project_id}")
def update_project(
    project_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    project = service.repo.get_by_id(db, project_id)
    return service.update_project(
        db, user, project, payload.get("name"), payload.get("description")
    )


@router.patch("/{project_id}/archive")
def archive_project(
    project_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    project = service.repo.get_by_id(db, project_id)
    return service.archive_project(db, user, project)


@router.delete("/{project_id}")
def delete_project(
    project_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    project = service.repo.get_by_id(db, project_id)
    service.delete_project(db, user, project)
    return {"message": "project_deleted"}


@router.delete("/{project_id}/members/{user_id}")
def remove_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    project = service.repo.get_by_id(db, project_id)

    member = service.repo.get_member(db, user_id, project_id)

    service.remove_member(db, user, project, member)

    return {"message": "member_removed"}
