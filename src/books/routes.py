from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from typing import List
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

# from src.books.books_data import books
from src.books.models import Book
from src.books.schemas import BookSchema, BookUpdateSchema, BookCreateSchema
from src.auth.schemas import UserResponseSchema
from src.db.main import get_session
from src.books.service import BookService
from src.auth.dependencies import access_token_bearer, get_current_user, require_admin, require_author, require_user


book_router = APIRouter()
book_service = BookService()

# ─── PUBLIC / ANY USER ─────────────────────────────────
@book_router.get("/books", response_model=List[BookSchema])
async def get_all_books(session:AsyncSession = Depends(get_session), user:UserResponseSchema=Depends(require_user))->List[Book]:
    return await book_service.get_all_books(session)

@book_router.get("/book/{book_uid}", response_model=BookSchema)
async def get_book(
    book_uid: str, session: AsyncSession=Depends(get_session),
    user:UserResponseSchema = Depends(require_user)) -> dict:
    print(user)
    book = await book_service.get_book(book_uid, session)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")
    return book


# ─── AUTHOR ONLY (Create own books) ────────────────────

@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=BookSchema)
async def create_a_book(
    book_data:BookCreateSchema,
    session: AsyncSession = Depends(get_session),
    user:UserResponseSchema = Depends(require_author))->dict:
    return await book_service.create_book(book_data, session)

@book_router.patch("/book/{book_uid}", response_model=BookSchema)
async def update_book(book_uid: str, book_update_data:BookUpdateSchema,
                    session: AsyncSession=Depends(get_session),
                    user:UserResponseSchema = Depends(require_author))->dict:
    updated_book = await book_service.update_book(book_uid, book_update_data, session)
    if not updated_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")
    return updated_book


# ─── ADMIN ONLY (Delete any book) ──────────────────────

@book_router.delete("/book/{book_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_uid:str, session: AsyncSession=Depends(get_session),
                      user:UserResponseSchema=Depends(require_admin)):
    deleted = await book_service.delete_book(book_uid, session) 
    
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")
    return None
