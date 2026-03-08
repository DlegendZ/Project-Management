import pytest
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.schemas.user import UpdateProfileRequest
from app.exceptions import ConflictException, NotFoundException, BadRequestException
from tests.conftest import create_test_user


def test_create_user_success(db: Session):
    user = UserService.create_user(db, "newuser", "new@example.com", "Password1")
    assert user.id is not None
    assert user.username == "newuser"
    assert user.email == "new@example.com"
    assert user.hashed_password != "Password1"


def test_create_user_duplicate_email_raises(db: Session):
    create_test_user(db, username="user1", email="dup@example.com")
    db.commit()
    with pytest.raises(ConflictException) as exc:
        UserService.create_user(db, "user2", "dup@example.com", "Password1")
    assert exc.value.code == "duplicate_email"


def test_create_user_duplicate_username_raises(db: Session):
    create_test_user(db, username="dupname", email="a@example.com")
    db.commit()
    with pytest.raises(ConflictException) as exc:
        UserService.create_user(db, "dupname", "b@example.com", "Password1")
    assert exc.value.code == "duplicate_username"


def test_get_user_by_id_not_found_raises(db: Session):
    with pytest.raises(NotFoundException):
        UserService.get_user_by_id(db, 99999)


def test_update_profile_username(db: Session):
    user = create_test_user(db, username="oldname", email="old@example.com")
    db.commit()
    updated = UserService.update_profile(
        db, user, UpdateProfileRequest(username="newname")
    )
    assert updated.username == "newname"


def test_update_profile_password_requires_current(db: Session):
    user = create_test_user(db)
    db.commit()
    with pytest.raises(BadRequestException):
        UserService.update_profile(
            db, user, UpdateProfileRequest(new_password="NewPass123")
        )


def test_update_profile_wrong_current_password_raises(db: Session):
    user = create_test_user(db, password="OldPass1")
    db.commit()
    with pytest.raises(BadRequestException):
        UserService.update_profile(
            db,
            user,
            UpdateProfileRequest(current_password="Wrong1", new_password="NewPass123"),
        )


def test_update_profile_same_password_raises(db: Session):
    user = create_test_user(db, password="SamePass1")
    db.commit()
    with pytest.raises(BadRequestException):
        UserService.update_profile(
            db,
            user,
            UpdateProfileRequest(
                current_password="SamePass1", new_password="SamePass1"
            ),
        )


def test_deactivate_user(db: Session):
    user = create_test_user(db, username="todeactivate", email="deactivate@example.com")
    db.commit()
    result = UserService.deactivate_user(db, user.id)
    assert result.is_active is False


def test_delete_user_not_found_raises(db: Session):
    with pytest.raises(NotFoundException):
        UserService.delete_user(db, 99999)
