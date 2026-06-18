from src.auth.models import User
from src.auth.schemas import UserCreateSchema, UserLoginSchema, UserResponseSchema
from src.auth.utils import generate_password_hash, verify_password
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
import uuid

class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        user = result.first()
        return user

    async def user_exists(self, email:str, session: AsyncSession):
        user = await self.get_user_by_email(email, session)
        return True if user is not None else False
    
    async def create_user(self, user_data: UserCreateSchema, session:AsyncSession):
        user_data_dict = user_data.model_dump()
        # username=user_data.username
        # first_name=user_data.first_name
        # last_name=user_data.last_name
        # email=user_data.email
        plain_password = user_data_dict.pop("password")
        # password_hash = generate_password_hash(plain_password)
        # new_user = User(
        #     username=username,
        #     first_name=first_name,
        #     last_name=last_name,
        #     email=email,
        #     password_hash=password_hash,
        #     is_verified=True
        # )
        new_user = User(**user_data_dict)
        new_user.password_hash = generate_password_hash(plain_password)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    
    async def get_user_by_uid(self, uid: str, session: AsyncSession):
        """Fetch user by UUID string."""
        uid_uuid = uuid.UUID(uid)  # Convert string to UUID object
        statement = select(User).where(User.uid == uid_uuid)
        result = await session.exec(statement)
        user = result.first()
        return user
