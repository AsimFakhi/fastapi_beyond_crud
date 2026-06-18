from sqlmodel import create_engine, text, SQLModel
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from src.config import CONF
import ssl
from src.books.models import Book

ssl_context = ssl.create_default_context()
engine = create_async_engine(
    url=CONF.DATABASE_URL,
    # echo = True,
    connect_args={"ssl": ssl_context},
    pool_pre_ping=True
    # For asyncpg: connect_args={"ssl": ssl_context}
    # For psycopg (async): connect_args={"sslmode": "require"} or similar
)


    
# Create session factory once (not inside the function!)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False # Optional: prevents implicit flushes
)

async def get_session():
    """Dependency to provide session object for FastAPI"""
    async with AsyncSessionLocal() as session:
        yield session
    

async def initdb():
    """Create connection and tables"""
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        # await conn.run_sync(SQLModel.metadata.create_all)
        statement = text("SELECT 'Bismillah!! Alhamdullaih DB seesion initiated.'")
        result = await conn.execute(statement)
        print(f"{'='*73}\n||DB Status =======>>>>> {result.scalar()}||\n{'='*73}")