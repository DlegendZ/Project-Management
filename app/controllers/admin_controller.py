from app.services.admin_services import AdminService
from app.database import get_db
from app import schema

from fastapi import Depends
from sqlalchemy.orm import Session

admin_service = AdminService()

async def view_users_controller(db: Session = Depends(get_db)):
    return await admin_service.view_users_service(db)

async def create_users_controller(user_schema: schema.UserCreate, db: Session = Depends(get_db)):
    return await admin_service.create_users_service(db, user_schema)