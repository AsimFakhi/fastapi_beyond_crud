from sqlmodel import create_engine, text, SQLModel
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker, AsyncEngine
from src.config import CONF
import ssl
from src.books.models import Book

ssl_context = ssl.create_default_context()
engine = create_async_engine(
    url=CONF.DATABASE_URL,
    echo = True,
    connect_args={"ssl": ssl_context}
)

# Below code is not right way to do because AsyncEngine is not a wrapper and we are trying to wrap sync by async
# engine = AsyncEngine(create_engine(
#     url=CONF.database_url,
#     echo = True,
#     connect_args={"ssl": ssl_context}
# ))

# Below will remove later as we will be using asyncio AsyncSession
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

async def initdb():
    """Create connection and tables"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        # statement = text("SELECT 'Bismillah!!'")
        # result = await conn.execute(statement)
        # print(result.all())