from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.users.models import User
from uuid import UUID
from sqlalchemy import select


class UserRepository:
    """
    Handles database operations for users.
    """


    def __init__(
        self,
        db: AsyncSession
    ):
        self.db = db



    async def get_by_email(
        self,
        email: str
    ) -> User | None:

        result = await self.db.execute(
            select(User)
            .where(
                User.email == email
            )
        )

        return result.scalar_one_or_none()



    async def create(
        self,
        user: User
    ) -> User:

        self.db.add(user)

        await self.db.commit()

        await self.db.refresh(user)

        return user
    



async def get_by_id(
    self,
    user_id: UUID
):

    result = await self.db.execute(
        select(User)
        .where(
            User.id == user_id
        )
    )

    return result.scalar_one_or_none()