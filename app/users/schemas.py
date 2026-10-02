from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


# ============================================================
# USER CREATION
# ============================================================

class UserCreate(BaseModel):
    """
    Schema used when creating a new user account.
    """

    first_name: str = Field(
        min_length=1,
        max_length=100,
        description="User's first name.",
    )

    last_name: str = Field(
        min_length=1,
        max_length=100,
        description="User's last name.",
    )

    email: EmailStr = Field(
        description="User's email address.",
    )

    password: str = Field(
        min_length=8,
        max_length=128,
        description="User's account password.",
    )

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, value: str) -> str:
        """
        Remove unnecessary spaces and prevent empty names.
        """

        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty.")

        return value


# ============================================================
# USER PROFILE UPDATE
# ============================================================

class UserUpdate(BaseModel):
    """
    Schema used when a user updates their profile.

    All fields are optional because the endpoint uses PATCH.
    """

    first_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated first name.",
    )

    last_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated last name.",
    )

    email: EmailStr | None = Field(
        default=None,
        description="Updated email address.",
    )

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, value: str | None) -> str | None:
        """
        Remove unnecessary spaces and prevent empty names.
        """

        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty.")

        return value


# ============================================================
# USER RESPONSE
# ============================================================

class UserResponse(BaseModel):
    """
    Schema returned by the API when exposing user information.
    """

    id: UUID

    first_name: str
    last_name: str

    email: EmailStr

    role: str

    is_active: bool
    is_verified: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )