from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.enums import UserRole
from app.users.models import User


class UserRepository:
    """
    Database operations for the User model.

    This class is responsible only for database access.
    Business rules and authorization belong in UserService.
    """

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    # ========================================================
    # GET BY EMAIL
    # ========================================================

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        """
        Retrieve a user by email address.

        Returns:
            User | None:
                The matching user or None when not found.
        """

        result = await self.db.execute(
            select(User).where(
                User.email == email
            )
        )

        return result.scalar_one_or_none()

    # ========================================================
    # GET BY ID
    # ========================================================

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:
        """
        Retrieve a user by UUID.

        Returns:
            User | None:
                The matching user or None when not found.
        """

        result = await self.db.execute(
            select(User).where(
                User.id == user_id
            )
        )

        return result.scalar_one_or_none()

    # ========================================================
    # GET ALL USERS
    # ========================================================

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """
        Retrieve a paginated list of users.

        Users are returned from newest to oldest based
        on created_at.
        """

        result = await self.db.execute(
            select(User)
            .order_by(
                User.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )

    # ========================================================
    # COUNT ACTIVE ADMINISTRATORS
    # ========================================================

    async def count_active_admins(self) -> int:
        """
        Count the number of active administrator accounts.

        This is used by UserService to protect the
        last active administrator from being:

        - demoted
        - deactivated
        - deleted
        """

        result = await self.db.execute(
            select(
                func.count(User.id)
            ).where(
                User.role == UserRole.ADMIN.value,
                User.is_active.is_(True),
            )
        )

        return int(
            result.scalar_one()
        )

    # ========================================================
    # CREATE
    # ========================================================

    async def create(
        self,
        user: User,
    ) -> User:
        """
        Persist a new user to the database.
        """

        self.db.add(user)

        await self.db.commit()

        await self.db.refresh(
            user
        )

        return user

    # ========================================================
    # UPDATE
    # ========================================================

    async def update(
        self,
        user: User,
    ) -> User:
        """
        Persist changes made to an existing user.
        """

        await self.db.commit()

        await self.db.refresh(
            user
        )

        return user

    # ========================================================
    # DELETE
    # ========================================================

    async def delete(
        self,
        user: User,
    ) -> None:
        """
        Permanently delete a user from the database.
        """

        await self.db.delete(
            user
        )

        await self.db.commit()

