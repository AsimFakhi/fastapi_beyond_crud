from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import date

class BookSchema(BaseModel):
    uid: UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str

class BookUpdateSchema(BaseModel):
    title: Optional [str] = None
    author: Optional [str] = None
    publisher: Optional [str] = None
    published_date: Optional[date] = None
    page_count: Optional [int] = None
    language: Optional [str] = None

    model_config = ConfigDict(extra="forbid")

class BookCreateSchema(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str