from pydantic import BaseModel, EmailStr

class UserResponse(BaseModel):
    username: str
    email: EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserUpdatePatch(BaseModel):
    username: str
    email: EmailStr
    password: str