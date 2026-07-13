from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.security import hash_password
from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserCreate


class AuthService:


    def __init__(
        self,
        db: AsyncSession
    ):
        self.user_repository = UserRepository(db)



    async def register(
        self,
        data: UserCreate
    ) -> User:


        existing_user = await self.user_repository.get_by_email(
            data.email
        )


        if existing_user:
            raise ValueError(
                "Email already registered"
            )


        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            password_hash=hash_password(
                data.password
            )
        )


        return await self.user_repository.create(user)