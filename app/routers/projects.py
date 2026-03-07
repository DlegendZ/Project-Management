from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, AddMemberRequest, ProjectMemberResponse
from app.schemas.common import PaginatedResponse
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=PaginatedResponse[ProjectResponse])
def list_projects(
    is_archived: Optional[bool] = Query(False),
    search: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    projects, total = ProjectService.list_projects(db, current_user, is_archived=is_archived, search=search, limit=limit, offset=offset)
    return PaginatedResponse(total=total, limit=limit, offset=offset, items=projects)


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ProjectService.create_project(db, current_user, data)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ProjectService.get_project(db, project_id, current_user)


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ProjectService.update_project(db, project_id, current_user, data)


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ProjectService.delete_project(db, project_id, current_user)


@router.patch("/{project_id}/archive", response_model=ProjectResponse)
def archive_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ProjectService.archive_project(db, project_id, current_user)


@router.get("/{project_id}/members", response_model=list[ProjectMemberResponse])
def list_members(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ProjectService.list_members(db, project_id, current_user)


@router.post("/{project_id}/members", response_model=ProjectMemberResponse, status_code=201)
def add_member(
    project_id: int,
    data: AddMemberRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ProjectService.add_member(db, project_id, current_user, data.user_id)


@router.delete("/{project_id}/members/{user_id}", status_code=204)
def remove_member(
    project_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ProjectService.remove_member(db, project_id, current_user, user_id)
