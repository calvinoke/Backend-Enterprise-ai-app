from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)

from app.auth.security import validate_password_strength
from app.users.enums import UserRole


# ============================================================
# PUBLIC USER CREATION
# ============================================================

class UserCreate(BaseModel):
    """
    Schema used for public registration.

    Public users cannot choose their role.
    They always start as USER.
    """

    first_name: str = Field(
        min_length=1,
        max_length=100,
    )

    last_name: str = Field(
        min_length=1,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Name cannot be empty."
            )

        return value


# ============================================================
# ADMIN USER CREATION
# ============================================================

class AdminUserCreate(BaseModel):
    """
    Schema used by administrators to create users.

    An administrator may choose whether the new account is
    USER or ADMIN.
    """

    first_name: str = Field(
        min_length=1,
        max_length=100,
    )

    last_name: str = Field(
        min_length=1,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    role: UserRole = Field(
        default=UserRole.USER,
    )

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Name cannot be empty."
            )

        return value

    @field_validator("password")
    @classmethod
    def validate_password(
        cls,
        value: str,
    ) -> str:
        return validate_password_strength(value)


# ============================================================
# USER PROFILE UPDATE
# ============================================================

class UserUpdate(BaseModel):
    """
    Schema for updating personal user information.

    Role, active status, and verification status cannot be
    modified through this schema.
    """

    first_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    email: EmailStr | None = Field(
        default=None,
    )

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(
        cls,
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError(
                "Name cannot be empty."
            )

        return value


# ============================================================
# ROLE UPDATE
# ============================================================

class UserRoleUpdate(BaseModel):
    """
    Schema used by administrators to change a user's role.
    """

    role: UserRole


# ============================================================
# USER RESPONSE
# ============================================================

class UserResponse(BaseModel):
    """
    User representation returned by the API.
    """

    id: UUID

    first_name: str
    last_name: str

    email: EmailStr

    role: UserRole

    is_active: bool
    is_verified: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )