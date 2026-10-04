"""Auth request/response schemas."""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=6)
    # Public self-registration must never grant staff or administrative access.
    role: Literal["farmer"] = "farmer"
    email: Optional[str] = None
    language_preference: str = Field(default="en")
    consent_given: bool = Field(default=False)


class LoginRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    password_change_required: bool = False


class RefreshRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(..., min_length=12, max_length=128)


class UserResponse(BaseModel):
    id: str
    name: str
    phone: str
    email: Optional[str] = None
    role: str
    language_preference: str
    is_active: bool
    password_change_required: bool = False

    model_config = ConfigDict(from_attributes=True)
