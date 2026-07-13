from datetime import datetime, timedelta, UTC
from typing import Any
import hashlib

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings


# Password hashing configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Hash plain password.

    bcrypt supports maximum 72 bytes.
    """

    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        raise ValueError(
            "Password cannot exceed 72 bytes"
        )

    return pwd_context.hash(password)



def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify password against stored hash.
    """

    return pwd_context.verify(
        plain_password,
        hashed_password,
    )



def create_access_token(
    subject: str,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """
    Create short-lived JWT access token.
    """

    expire = (
        datetime.now(UTC)
        +
        timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )


    payload = {
        "sub": subject,
        "exp": expire,
        "type": "access",
    }


    if extra_claims:
        payload.update(extra_claims)


    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )



def create_refresh_token(
    subject: str,
) -> str:
    """
    Create long-lived refresh token.
    """

    expire = (
        datetime.now(UTC)
        +
        timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    )


    payload = {
        "sub": subject,
        "exp": expire,
        "type": "refresh",
    }


    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )



def decode_token(
    token: str,
) -> dict[str, Any] | None:
    """
    Decode JWT token.
    """

    try:

        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[
                settings.ALGORITHM
            ],
        )


    except JWTError:

        return None



def decode_refresh_token(
    token: str,
) -> dict[str, Any] | None:
    """
    Decode and validate refresh token only.
    """

    payload = decode_token(token)


    if not payload:
        return None


    if payload.get("type") != "refresh":
        return None


    return payload



def hash_refresh_token(
    token: str,
) -> str:
    """
    Hash refresh token before storing in database.
    """

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()