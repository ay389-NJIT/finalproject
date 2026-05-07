from redis import asyncio as aioredis
from app.core.config import settings

redis_client = None

async def get_redis_client():
    """Get or create Redis client"""
    global redis_client
    if redis_client is None:
        redis_client = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client

async def add_to_blacklist(token: str, expiry: int):
    """Add token to blacklist with expiration"""
    client = await get_redis_client()
    await client.setex(f"blacklist:{token}", expiry, "1")

async def is_blacklisted(token: str) -> bool:
    """Check if token is blacklisted"""
    client = await get_redis_client()
    result = await client.get(f"blacklist:{token}")
    return result is not None