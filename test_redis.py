import asyncio
from src.db.redis import redis_client

async def test():
    await redis_client.ping()
    print("Redis connected!")

asyncio.run(test())