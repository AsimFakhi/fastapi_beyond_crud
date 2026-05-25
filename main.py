from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.books.routes import book_router
from src.auth.routes import auth_router
from src.db.main import initdb

version = 'v1'
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server is starting...")
    await initdb()
    yield 
    # await engine.dispose()
    print("Server is stopping...")

app = FastAPI(
    title='FastAPI beyond CRUD',
    description='A RESTful API for a book review web service',
    version=version,
    lifespan=lifespan
)

app.include_router(book_router, prefix=f'/api/{version}/books', tags=['books'])
app.include_router(auth_router, prefix=f'/api/{version}/auth', tags=['auth'])



