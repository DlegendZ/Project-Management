from fastapi import FastAPI
from app.router.admin_router import router as admin_router
app = FastAPI()
app.include_router(admin_router)
