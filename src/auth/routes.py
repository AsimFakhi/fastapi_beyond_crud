from fastapi import APIRouter, Depends, status
from src.auth.schemas import UserCreateSchema, UserResponseSchema
from src.auth.service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException

auth_router = APIRouter()
user_service = UserService()


@auth_router.post("/signup", 
                  response_model=UserResponseSchema, 
                  status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data:UserCreateSchema, session:AsyncSession =Depends(get_session)):
    email=user_data.email
    user_exist = await user_service.user_exists(email, session)
    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with email already exists."
        )
    new_user = await user_service.create_user(user_data, session)
    return new_user
