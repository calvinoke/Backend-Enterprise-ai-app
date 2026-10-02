from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import User


class UserRepository:
    """
    Database operations for the User model.
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
        result = await self.db.execute(
            select(User)
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )

    # ========================================================
    # CREATE
    # ========================================================

    async def create(
        self,
        user: User,
    ) -> User:
        self.db.add(user)

        await self.db.commit()

        await self.db.refresh(user)

        return user

    # ========================================================
    # UPDATE
    # ========================================================

    async def update(
        self,
        user: User,
    ) -> User:
        await self.db.commit()

        await self.db.refresh(user)

        return user

    # ========================================================
    # DELETE
    # ========================================================

    async def delete(
        self,
        user: User,
    ) -> None:
        await self.db.delete(user)

        await self.db.commit()