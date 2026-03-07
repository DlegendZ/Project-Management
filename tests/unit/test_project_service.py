import pytest
from sqlalchemy.orm import Session
from app.services.project_service import ProjectService
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.exceptions import ForbiddenException, NotFoundException, ConflictException
from app.models.user import UserRole
from tests.conftest import create_test_user


def make_project(db, user, name="My Project"):
    return ProjectService.create_project(db, user, ProjectCreate(name=name))


def test_create_project_sets_owner(db: Session):
    user = create_test_user(db)
    db.commit()
    project = make_project(db, user)
    assert project.owner_id == user.id


def test_create_project_adds_owner_as_member(db: Session):
    from app.repositories.project_repository import ProjectRepository
    user = create_test_user(db)
    db.commit()
    project = make_project(db, user)
    member = ProjectRepository.get_member(db, project.id, user.id)
    assert member is not None


def test_update_project_by_non_owner_raises(db: Session):
    owner = create_test_user(db, username="owner", email="owner@example.com")
    other = create_test_user(db, username="other", email="other@example.com")
    db.commit()
    project = make_project(db, owner)
    with pytest.raises(ForbiddenException):
        ProjectService.update_project(db, project.id, other, ProjectUpdate(name="New Name"))


def test_archive_project_toggles(db: Session):
    user = create_test_user(db)
    db.commit()
    project = make_project(db, user)
    assert project.is_archived is False
    archived = ProjectService.archive_project(db, project.id, user)
    assert archived.is_archived is True
    unarchived = ProjectService.archive_project(db, project.id, user)
    assert unarchived.is_archived is False


def test_add_member_duplicate_raises(db: Session):
    owner = create_test_user(db, username="owner2", email="owner2@example.com")
    member_user = create_test_user(db, username="mem1", email="mem1@example.com")
    db.commit()
    project = make_project(db, owner)
    ProjectService.add_member(db, project.id, owner, member_user.id)
    with pytest.raises(ConflictException):
        ProjectService.add_member(db, project.id, owner, member_user.id)


def test_remove_member_not_found_raises(db: Session):
    owner = create_test_user(db, username="owner3", email="owner3@example.com")
    db.commit()
    project = make_project(db, owner)
    with pytest.raises(NotFoundException):
        ProjectService.remove_member(db, project.id, owner, 99999)


def test_delete_project_by_non_owner_raises(db: Session):
    owner = create_test_user(db, username="owner4", email="owner4@example.com")
    other = create_test_user(db, username="other4", email="other4@example.com")
    db.commit()
    project = make_project(db, owner)
    with pytest.raises(ForbiddenException):
        ProjectService.delete_project(db, project.id, other)


def test_admin_can_update_any_project(db: Session):
    owner = create_test_user(db, username="owner5", email="owner5@example.com")
    admin = create_test_user(db, username="adm", email="adm@example.com", role=UserRole.admin)
    db.commit()
    project = make_project(db, owner)
    updated = ProjectService.update_project(db, project.id, admin, ProjectUpdate(name="Admin Updated"))
    assert updated.name == "Admin Updated"
