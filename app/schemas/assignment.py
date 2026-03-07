from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.user import UserResponse


class AssignRequest(BaseModel):
    user_id: int


class AssignmentResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    assigned_by: int
    assigned_at: datetime
    assignee: Optional[UserResponse] = None

    model_config = {"from_attributes": True}
