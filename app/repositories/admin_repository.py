from app import models
from sqlalchemy.orm import Session

class AdminRepository:

    def view_users_repo(self, db: Session):
        return db.query(models.User).all()

    def create_users_repo(self, db: Session, user_model: models.User):
        db.add(user_model)
        db.commit()
        db.refresh(user_model)
        return user_model

