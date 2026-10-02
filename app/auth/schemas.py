from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):

    first_name: str = Field(
        min_length=2,
        max_length=100
    )

    last_name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=100
    )


class LoginRequest(BaseModel):

    email: EmailStr

    password: str
    

class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


#Efrom pydantic import BaseModel, EmailStr, Field


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str


class ResetPasswordRequest(BaseModel):
    token: str = Field(
        min_length=20
    )

    new_password: str = Field(
        min_length=8,
        max_length=128,
    )


class ResetPasswordResponse(BaseModel):
    message: str

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.auth.security import validate_password_strength


# =========================================
# CHANGE PASSWORD
# =========================================

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(
        min_length=1,
        max_length=128,
    )

    new_password: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password(
        cls,
        value: str,
    ) -> str:

        return validate_password_strength(
            value
        )


class ChangePasswordResponse(BaseModel):
    message: str


# =========================================
# EMAIL VERIFICATION
# =========================================

class VerifyEmailRequest(BaseModel):
    token: str = Field(
        min_length=20,
    )


class VerifyEmailResponse(BaseModel):
    message: str


# =========================================
# RESEND VERIFICATION
# =========================================

class ResendVerificationRequest(BaseModel):
    email: EmailStr


class ResendVerificationResponse(BaseModel):
    message: str

