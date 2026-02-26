from fastapi import APIRouter
from app.controllers import admin_controller

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

router.get("/users")(admin_controller.view_users_controller)