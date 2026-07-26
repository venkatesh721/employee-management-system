from uuid import UUID
from typing import Literal

import re

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=72)
    role: Literal["admin", "employee"]

    @field_validator("identifier", mode="before")
    @classmethod
    def normalize_identifier(cls, value):
        return value.strip().lower() if isinstance(value, str) else value


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=150, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=6, max_length=72)
    full_name: str = Field(min_length=1, max_length=255)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("username", "full_name", mode="before")
    @classmethod
    def strip_text_fields(cls, value):
        return value.strip() if isinstance(value, str) else value


class UpdateUserRequest(BaseModel):
    email: EmailStr | None = None
    username: str | None = Field(
        default=None, min_length=3, max_length=150, pattern=r"^[A-Za-z0-9_.-]+$"
    )
    password: str | None = Field(default=None, min_length=6, max_length=72)
    full_name: str | None = Field(default=None, min_length=1, max_length=255)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("username", "full_name", mode="before")
    @classmethod
    def strip_text_fields(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("password")
    @classmethod
    def enforce_updated_password_strength(cls, value):
        if value is None:
            return value
        checks = [r"[A-Z]", r"[a-z]", r"\d", r"[^A-Za-z0-9]"]
        if not all(re.search(pattern, value) for pattern in checks):
            raise ValueError(
                "Password must contain uppercase, lowercase, number, and special character"
            )
        return value


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    full_name: str | None
    phone: str | None
    role: Literal["admin", "employee"]
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


def validate_strong_password(password: str) -> str:
    checks = [
        (r"[A-Z]", "one uppercase letter"),
        (r"[a-z]", "one lowercase letter"),
        (r"\d", "one number"),
        (r"[^A-Za-z0-9]", "one special character"),
    ]
    missing = [
        message for pattern, message in checks if not re.search(pattern, password)
    ]
    if missing:
        raise ValueError(f"Password must contain {', '.join(missing)}")
    return password


class EmployeeRegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str = Field(min_length=2, max_length=255)
    username: str = Field(min_length=3, max_length=150, pattern=r"^[A-Za-z0-9_.-]+$")
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)
    password: str = Field(min_length=8, max_length=72)
    confirm_password: str = Field(min_length=8, max_length=72)
    accept_terms: bool

    @field_validator("email", mode="before")
    @classmethod
    def normalize_registration_email(cls, value):
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("username", "full_name", "phone", mode="before")
    @classmethod
    def strip_registration_fields(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("password")
    @classmethod
    def enforce_password_strength(cls, value):
        return validate_strong_password(value)

    @model_validator(mode="after")
    def validate_confirmation_and_terms(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        if not self.accept_terms:
            raise ValueError("You must accept the terms")
        return self


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=32, max_length=512)
    password: str = Field(min_length=8, max_length=72)
    confirm_password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def enforce_password_strength(cls, value):
        return validate_strong_password(value)

    @model_validator(mode="after")
    def validate_confirmation(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self
