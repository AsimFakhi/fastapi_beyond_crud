from fastapi import FastAPI
from src.books.routes import book_router
from src.db.main import initdb
from contextlib import asynccontextmanager

version = 'v1'
@asynccontextmanager
async def lifespan(app:FastAPI):
    print("Server is starting...")
    await initdb()
    yield 
    print("Server is stopping...")

app = FastAPI(
    title='FastAPI beyond CRUD',
    description='A RESTful API for a book review web service',
    version=version,
    lifespan=lifespan
)

app.include_router(book_router, prefix=f'/api/{version}/books', tags=['books'])



