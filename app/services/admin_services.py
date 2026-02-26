from app.repositories.admin_repository import AdminRepository

class adminService:

    def __init__(self):
        self.admin_repository = AdminRepository()

    async def view_users_service(self, db):
        return self.admin_repository.view_users_repo(db)
