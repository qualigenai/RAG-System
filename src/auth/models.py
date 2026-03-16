from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class APIKeyCreate(BaseModel):
    name: str
    expires_in: str = "never"


class APIKeyResponse(BaseModel):
    id: str
    name: str
    last_used: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True