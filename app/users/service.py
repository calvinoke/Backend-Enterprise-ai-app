from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import hash_password
from app.users.enums import UserRole
from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import (
    AdminUserCreate,
    UserRoleUpdate,
    UserUpdate,
)


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
    # INTERNAL ADMIN CHECK
    # ========================================================

    @staticmethod
    def _is_admin(user: User) -> bool:
        """
        Return True when the supplied user is an administrator.
        """

        return user.role == UserRole.ADMIN.value

    # ========================================================
    # REQUIRE ADMIN
    # ========================================================

    def _require_admin(
        self,
        current_admin: User,
    ) -> None:
        """
        Ensure the current user has administrator privileges.
        """

        if not self._is_admin(current_admin):
            raise PermissionError(
                "Administrator access required."
            )

    # ========================================================
    # PREVENT LAST ACTIVE ADMIN FROM BEING REMOVED
    # ========================================================

    async def _ensure_not_last_active_admin(
        self,
        target_user: User,
    ) -> None:
        """
        Prevent the last active administrator from being:

        - demoted
        - deactivated
        - deleted
        """

        if (
            target_user.role == UserRole.ADMIN.value
            and target_user.is_active
        ):
            active_admin_count = (
                await self.repository.count_active_admins()
            )

            if active_admin_count <= 1:
                raise PermissionError(
                    "The last active administrator cannot be removed "
                    "or have administrator privileges disabled."
                )

    # ========================================================
    # GET CURRENT USER
    # ========================================================

    async def get_current_user(
        self,
        user_id: UUID,
    ) -> User:
        """
        Return a user by ID.

        Raises ValueError when the user does not exist.
        """

        user = await self.repository.get_by_id(
            user_id
        )

        if not user:
            raise ValueError(
                "User not found."
            )

        return user

    # ========================================================
    # CREATE USER - ADMIN ONLY
    # ========================================================

    async def create_user(
        self,
        current_admin: User,
        data: AdminUserCreate,
    ) -> User:
        """
        Allow an administrator to create a user account.

        The administrator may create either a USER
        or ADMIN account.
        """

        self._require_admin(
            current_admin
        )

        email = (
            str(data.email)
            .strip()
            .lower()
        )

        # ----------------------------------------------------
        # Check whether the email already exists
        # ----------------------------------------------------

        existing_user = (
            await self.repository.get_by_email(
                email
            )
        )

        if existing_user:
            raise ValueError(
                "Email address is already registered."
            )

        # ----------------------------------------------------
        # Create user
        # ----------------------------------------------------

        user = User(
            first_name=data.first_name.strip(),
            last_name=data.last_name.strip(),
            email=email,
            password_hash=hash_password(
                data.password
            ),
            role=data.role.value,
            is_active=True,
            is_verified=False,
        )

        try:
            return await self.repository.create(
                user
            )

        except IntegrityError:
            await self.db.rollback()

            raise ValueError(
                "Unable to create user because "
                "the email address may already be in use."
            )

    # ========================================================
    # GET ALL USERS
    # ========================================================

    async def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """
        Return a paginated list of users.
        """

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
        """
        Return a user by UUID.
        """

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
        """
        Update basic user profile information.

        Role changes are deliberately excluded.
        Use update_user_role() for role changes.
        """

        # ----------------------------------------------------
        # First name
        # ----------------------------------------------------

        if data.first_name is not None:
            first_name = data.first_name.strip()

            if not first_name:
                raise ValueError(
                    "First name cannot be empty."
                )

            user.first_name = first_name

        # ----------------------------------------------------
        # Last name
        # ----------------------------------------------------

        if data.last_name is not None:
            last_name = data.last_name.strip()

            if not last_name:
                raise ValueError(
                    "Last name cannot be empty."
                )

            user.last_name = last_name

        # ----------------------------------------------------
        # Email
        # ----------------------------------------------------

        if data.email is not None:
            new_email = (
                str(data.email)
                .strip()
                .lower()
            )

            if not new_email:
                raise ValueError(
                    "Email address cannot be empty."
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

                # Changing the email address means
                # the new email must be verified again.
                user.is_verified = False

        # ----------------------------------------------------
        # Save changes
        # ----------------------------------------------------

        try:
            return await self.repository.update(
                user
            )

        except IntegrityError:
            await self.db.rollback()

            raise ValueError(
                "Unable to update user because the email "
                "address may already be in use."
            )

    # ========================================================
    # UPDATE USER ROLE - ADMIN ONLY
    # ========================================================

    async def update_user_role(
        self,
        current_admin: User,
        target_user_id: UUID,
        role: UserRole,
    ) -> User:
        """
        Change a user's role.

        Allowed roles:

        - user
        - admin

        Administrators cannot change their own role.

        The last active administrator cannot be
        demoted to a normal user.
        """

        # ----------------------------------------------------
        # Require administrator
        # ----------------------------------------------------

        self._require_admin(
            current_admin
        )

        # ----------------------------------------------------
        # Prevent changing own role
        # ----------------------------------------------------

        if current_admin.id == target_user_id:
            raise PermissionError(
                "Administrators cannot change their own role."
            )

        # ----------------------------------------------------
        # Find target user
        # ----------------------------------------------------

        target_user = (
            await self.repository.get_by_id(
                target_user_id
            )
        )

        if not target_user:
            raise ValueError(
                "User not found."
            )

        # ----------------------------------------------------
        # Normalize role
        # ----------------------------------------------------

        new_role = (
            role.value
            if isinstance(role, UserRole)
            else str(role)
        )

        if new_role not in {
            UserRole.USER.value,
            UserRole.ADMIN.value,
        }:
            raise ValueError(
                "Invalid user role."
            )

        # ----------------------------------------------------
        # If there is no actual change, return the user.
        # ----------------------------------------------------

        if target_user.role == new_role:
            return target_user

        # ----------------------------------------------------
        # Prevent demotion of the last active admin.
        # ----------------------------------------------------

        if (
            target_user.role == UserRole.ADMIN.value
            and target_user.is_active
            and new_role == UserRole.USER.value
        ):
            await self._ensure_not_last_active_admin(
                target_user
            )

        # ----------------------------------------------------
        # Update role
        # ----------------------------------------------------

        target_user.role = new_role

        try:
            return await self.repository.update(
                target_user
            )

        except IntegrityError:
            await self.db.rollback()

            raise ValueError(
                "Unable to update the user's role."
            )

    # ========================================================
    # ACTIVATE USER - ADMIN ONLY
    # ========================================================

    async def activate_user(
        self,
        current_admin: User,
        target_user_id: UUID,
    ) -> User:
        """
        Activate a user account.
        """

        self._require_admin(
            current_admin
        )

        # ----------------------------------------------------
        # Find target user
        # ----------------------------------------------------

        target_user = (
            await self.repository.get_by_id(
                target_user_id
            )
        )

        if not target_user:
            raise ValueError(
                "User not found."
            )

        # ----------------------------------------------------
        # Already active
        # ----------------------------------------------------

        if target_user.is_active:
            return target_user

        # ----------------------------------------------------
        # Activate
        # ----------------------------------------------------

        target_user.is_active = True

        try:
            return await self.repository.update(
                target_user
            )

        except IntegrityError:
            await self.db.rollback()

            raise ValueError(
                "Unable to activate user."
            )

    # ========================================================
    # DEACTIVATE USER - ADMIN ONLY
    # ========================================================

    async def deactivate_user(
        self,
        current_admin: User,
        target_user_id: UUID,
    ) -> User:
        """
        Deactivate a user account.

        Administrators cannot deactivate themselves.

        The last active administrator cannot be deactivated.
        """

        self._require_admin(
            current_admin
        )

        # ----------------------------------------------------
        # Prevent administrator from deactivating themselves
        # ----------------------------------------------------

        if current_admin.id == target_user_id:
            raise ValueError(
                "Administrators cannot deactivate their own account."
            )

        # ----------------------------------------------------
        # Find target user
        # ----------------------------------------------------

        target_user = (
            await self.repository.get_by_id(
                target_user_id
            )
        )

        if not target_user:
            raise ValueError(
                "User not found."
            )

        # ----------------------------------------------------
        # Already inactive
        # ----------------------------------------------------

        if not target_user.is_active:
            return target_user

        # ----------------------------------------------------
        # Protect the last active administrator
        # ----------------------------------------------------

        await self._ensure_not_last_active_admin(
            target_user
        )

        # ----------------------------------------------------
        # Deactivate
        # ----------------------------------------------------

        target_user.is_active = False

        try:
            return await self.repository.update(
                target_user
            )

        except IntegrityError:
            await self.db.rollback()

            raise ValueError(
                "Unable to deactivate user."
            )

    # ========================================================
    # DELETE USER - ADMIN ONLY
    # ========================================================

    async def delete_user(
        self,
        current_admin: User,
        target_user_id: UUID,
    ) -> None:
        """
        Permanently delete a user account.

        Administrators cannot delete themselves.

        The last active administrator cannot be deleted.
        """

        self._require_admin(
            current_admin
        )

        # ----------------------------------------------------
        # Prevent administrator from deleting themselves
        # ----------------------------------------------------

        if current_admin.id == target_user_id:
            raise ValueError(
                "Administrators cannot delete their own account."
            )

        # ----------------------------------------------------
        # Find target user
        # ----------------------------------------------------

        target_user = (
            await self.repository.get_by_id(
                target_user_id
            )
        )

        if not target_user:
            raise ValueError(
                "User not found."
            )

        # ----------------------------------------------------
        # Protect the last active administrator
        # ----------------------------------------------------

        await self._ensure_not_last_active_admin(
            target_user
        )

        # ----------------------------------------------------
        # Delete target user
        # ----------------------------------------------------

        try:
            await self.repository.delete(
                target_user
            )

        except IntegrityError:
            await self.db.rollback()

            raise ValueError(
                "Unable to delete user because "
                "related records may still exist."
            )

