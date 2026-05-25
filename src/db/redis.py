try:
    from redis import asyncio as aioredis
except ImportError:
    import aioredis 
from src.config import CONF


# Singlton connection pool
redis_client =aioredis.Redis(
    host = CONF.REDIS_HOST,
    port = CONF.REDIS_PORT,
    password=CONF.REDIS_PASSWORD,
    db=0,
    decode_responses=True
)

async def add_jti_to_blocklist(jti:str, expiry:int) ->None:
    """
    Add a JTI (JWT ID) to the blocklist.
    Expiry should match or exceed the token's remaining lifetime.
    """
    await redis_client.set(name=f"bl:{jti}", value="revoked", ex=expiry)

async def token_in_blocklist(jti: str) -> bool:
    """Check if a JTI is in the blocklist."""
    result = await redis_client.get(f"bl:{jti}")
    return result is not None


async def close_redis():
    """Call this during app shutdown."""
    await redis_client.close()