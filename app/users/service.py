from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.enums import UserRole
from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserUpdate


class UserService:
    """
    Business logic for user management.
    """

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db
        self.repository = UserRepository(db)

    # ========================================================
    # GET CURRENT USER
    # ========================================================

    async def get_current_user(
        self,
        user_id: UUID,
    ) -> User:
        user = await self.repository.get_by_id(
            user_id
        )

        if not user:
            raise ValueError(
                "User not found."
            )

        return user

    # ========================================================
    # GET ALL USERS
    # ========================================================

    async def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        return await self.repository.get_all(
            skip=skip,
            limit=limit,
        )

    # ========================================================
    # GET USER BY ID
    # ========================================================

    async def get_user_by_id(
        self,
        user_id: UUID,
    ) -> User:
        user = await self.repository.get_by_id(
            user_id
        )

        if not user:
            raise ValueError(
                "User not found."
            )

        return user

    # ========================================================
    # UPDATE USER
    # ========================================================

    async def update_user(
        self,
        user: User,
        data: UserUpdate,
    ) -> User:
        # ----------------------------------------------------
        # First name
        # ----------------------------------------------------

        if data.first_name is not None:
            user.first_name = data.first_name.strip()

        # ----------------------------------------------------
        # Last name
        # ----------------------------------------------------

        if data.last_name is not None:
            user.last_name = data.last_name.strip()

        # ----------------------------------------------------
        # Email
        # ----------------------------------------------------

        if data.email is not None:
            new_email = (
                str(data.email)
                .strip()
                .lower()
            )

            if new_email != user.email:
                existing_user = (
                    await self.repository.get_by_email(
                        new_email
                    )
                )

                if (
                    existing_user
                    and existing_user.id != user.id
                ):
                    raise ValueError(
                        "Email address is already in use."
                    )

                user.email = new_email

                # ------------------------------------------------
                # Changing email means the new address should
                # eventually be verified again.
                # ------------------------------------------------

                user.is_verified = False

        try:
            return await self.repository.update(
                user
            )

        except IntegrityError:
            await self.db.rollback()

            raise ValueError(
                "Unable to update user because the email address "
                "may already be in use."
            )

    # ========================================================
    # DELETE USER
    # ========================================================

    async def delete_user(
        self,
        current_admin: User,
        target_user_id: UUID,
    ) -> None:
        # ----------------------------------------------------
        # Admin check
        # ----------------------------------------------------

        if current_admin.role != UserRole.ADMIN.value:
            raise PermissionError(
                "Administrator access required."
            )

        # ----------------------------------------------------
        # Prevent admin from deleting themselves
        # ----------------------------------------------------

        if current_admin.id == target_user_id:
            raise ValueError(
                "Administrators cannot delete their own account."
            )

        # ----------------------------------------------------
        # Find target user
        # ----------------------------------------------------

        target_user = await self.repository.get_by_id(
            target_user_id
        )

        if not target_user:
            raise ValueError(
                "User not found."
            )

        # ----------------------------------------------------
        # Delete target
        # ----------------------------------------------------

        await self.repository.delete(
            target_user
        )

    # ========================================================
    # ACTIVATE USER
    # ========================================================

    async def activate_user(
        self,
        current_admin: User,
        target_user_id: UUID,
    ) -> User:
        if current_admin.role != UserRole.ADMIN.value:
            raise PermissionError(
                "Administrator access required."
            )

        target_user = await self.repository.get_by_id(
            target_user_id
        )

        if not target_user:
            raise ValueError(
                "User not found."
            )

        target_user.is_active = True

        return await self.repository.update(
            target_user
        )

    # ========================================================
    # DEACTIVATE USER
    # ========================================================

    async def deactivate_user(
        self,
        current_admin: User,
        target_user_id: UUID,
    ) -> User:
        if current_admin.role != UserRole.ADMIN.value:
            raise PermissionError(
                "Administrator access required."
            )

        # ----------------------------------------------------
        # Prevent administrator from deactivating themselves
        # ----------------------------------------------------

        if current_admin.id == target_user_id:
            raise ValueError(
                "Administrators cannot deactivate their own account."
            )

        target_user = await self.repository.get_by_id(
            target_user_id
        )

        if not target_user:
            raise ValueError(
                "User not found."
            )

        target_user.is_active = False

        return await self.repository.update(
            target_user
        )