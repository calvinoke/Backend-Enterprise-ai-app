from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import RefreshToken


class RefreshTokenRepository:


    def __init__(
        self,
        db: AsyncSession
    ):
        self.db = db



    async def create(
        self,
        token: RefreshToken
    ):

        self.db.add(token)

        await self.db.commit()

        await self.db.refresh(token)

        return token



    async def get_by_hash(
        self,
        token_hash: str,
    ):

        result = await self.db.execute(
            select(RefreshToken)
            .where(
                RefreshToken.token_hash == token_hash
            )
        )

        return result.scalar_one_or_none()



    async def revoke_by_hash(
        self,
        token_hash: str,
    ):

        token = await self.get_by_hash(
            token_hash
        )


        if not token:
            raise ValueError(
                "Refresh token not found"
            )


        token.revoked = True


        await self.db.commit()


        return token