from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID
from datetime import datetime

class UserCreateSchema(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    first_name: str = Field(min_length=1, max_length=20)
    last_name: str = Field(min_length=1, max_length=20)
    email: EmailStr
    password: str = Field(min_length=4)

class UserResponseSchema(BaseModel):
    uid: UUID
    username: str
    first_name: str
    last_name: str
    email: str
    is_verified: bool
    created_at: datetime 
    updated_at: datetime   
    model_config = ConfigDict(from_attributes=True, exclude={"password_hash"})

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class TokenUserData(BaseModel):
    uid: str
    email: str
    username: str | None = None