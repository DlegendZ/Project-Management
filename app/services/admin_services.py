from app.repositories.admin_repository import AdminRepository
from app import models, schema

class AdminService:

    def __init__(self):
        self.admin_repository = AdminRepository()

    async def view_users_service(self, db):
        return self.admin_repository.view_users_repo(db)

    async def create_users_service(self, db, user_schema: schema.UserCreate):
        user_model = models.User(
            username=user_schema.username,
            email=user_schema.email,
            hashed_password= user_schema.password
        )
        return self.admin_repository.create_users_repo(db, user_model)