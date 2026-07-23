from typing import cast

from redis.asyncio import Redis


def create_redis_client(url: str) -> Redis:
    """Create a lazy async Redis client owned by the application lifespan."""
    return cast(Redis, Redis.from_url(url, decode_responses=True))
