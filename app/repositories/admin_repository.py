from app import models
from sqlalchemy.orm import Session

class AdminRepository:

    def view_users_repo(self, db: Session):
        return db.query(models.User).all()

