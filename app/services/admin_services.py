from app.repositories.admin_repository import AdminRepository
from app import models
from app.utils import ensure_found, normalize_limit


class AdminService:

    # ------------------------
    # User Management
    # ------------------------

    def __init__(self):
        self.repo = AdminRepository()

    def get_user_by_id_service(self, db, user_id: int) -> models.User:
        user = self.repo.get_user_by_id_repo(db, user_id)
        ensure_found(user)
        return user

    def list_users_service(
        self, db, limit: int | None = None, offset: int | None = None
    ) -> list[models.User]:
        limit = normalize_limit(limit)
        return self.repo.list_users_repo(db, limit, offset)

    def deactivate_user_service(self, db, user_id: int) -> models.User:
        user = self.get_user_by_id_service(db, user_id)
        ensure_found(user)
        return self.repo.deactivate_user_repo(db, user)

    def delete_user_service(self, db, user_id: int) -> None:
        user = self.get_user_by_id_service(db, user_id)
        ensure_found(user)
        return self.repo.delete_user_repo(db, user)

    # def update_user_profile_service(self, db, user_id: int, username: str | None = None, email: str | N)
