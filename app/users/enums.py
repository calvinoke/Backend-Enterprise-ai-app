from enum import Enum


class UserRole(str, Enum):
    """
    Supported application roles.

    Roles are deliberately limited to the values defined here.
    """

    USER = "user"
    ADMIN = "admin"