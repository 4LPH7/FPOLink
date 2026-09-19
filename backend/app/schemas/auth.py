"""Auth request/response schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=6)
    role: str = Field(default="farmer")  # admin, fpo_staff, farmer, buyer
    email: Optional[str] = None
    language_preference: str = Field(default="en")
    consent_given: bool = Field(default=False)


class LoginRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    name: str
    phone: str
    email: Optional[str] = None
    role: str
    language_preference: str
    is_active: bool

    class Config:
        from_attributes = True
