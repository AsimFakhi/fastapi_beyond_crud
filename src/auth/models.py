from sqlmodel import SQLModel, Field, Column, func
import sqlalchemy.dialects.postgresql as pg
import uuid
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__="user_accounts"
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            unique=True,
            nullable=False,
            default=uuid.uuid4,
            info={"description":"Unique identifier for the user account."}
        )
    )
    username: str
    first_name: str
    last_name: str
    is_verified: bool = False
    email: str
    password_hash: str
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP ,default=datetime.now, onupdate=datetime.now))

    def __repr__(self) -> str:
        return f"<User {self.username}>"