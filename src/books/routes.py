from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from typing import List

from src.books.books_data import books
from src.books.schemas import BookSchema, BookUpdateSchema

book_router = APIRouter()


@book_router.get("/books", response_model=List[BookSchema])
async def get_all_books():
    return books

@book_router.get("/book/{book_id}")
async def get_book(book_id: int) -> dict:
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")

@book_router.patch("/book/{book_id}")
async def update_book(book_id: int, book_update_data:BookUpdateSchema):
    for book in books:
        if book["id"] == book_id:
            book["title"] = book_update_data.title
            book["publisher"] = book_update_data.publisher
            book["page_count"] = book_update_data.page_count
            book["language"] = book_update_data.language

            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")

@book_router.delete("/book/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id:int):
    for book in books:
        if book["id"] == book_id:
            books.remove(book)
            return {}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")