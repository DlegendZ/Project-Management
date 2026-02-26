from fastapi import APIRouter
from app.controllers import admin_controller
from app import schema

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

router.get("/users", response_model=list[schema.UserResponse])(admin_controller.view_users_controller)
router.post("/users", response_model=schema.UserResponse)(admin_controller.create_users_controller)