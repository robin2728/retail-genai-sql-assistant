from cache.redis_client import redis_client
from config import RATE_LIMIT, RATE_WINDOW

async def check_rate_limit(user_id: str):

    key = f"rate:{user_id}"

    current_count = await redis_client.incr(key)

    if current_count == 1:
        await redis_client.expire(key, RATE_WINDOW)

    if current_count > RATE_LIMIT:
        return False

    return True