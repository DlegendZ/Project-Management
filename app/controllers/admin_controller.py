from app.services.admin_services import adminService
from app.database import get_db

from fastapi import Depends
from sqlalchemy.orm import Session

async def view_users_controller(db: Session = Depends(get_db)):
    return adminService.view_users_service(db)

