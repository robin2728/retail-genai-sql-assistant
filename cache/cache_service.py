import hashlib
import json
import re

from cache.redis_client import redis_client
from config import CACHE_TTL

def normalize_sql(sql: str):

    sql = re.sub(r"\s+", " ", sql.strip())

    return sql.lower()

def generate_cache_key(sql: str):

    normalized = normalize_sql(sql)

    hashed = hashlib.sha256(
        normalized.encode()
    ).hexdigest()

    return f"sql:{hashed}"

async def get_cache(key: str):

    data = await redis_client.get(key)

    if data:
        return json.loads(data)

    return None

async def set_cache(key: str, value: dict):

    await redis_client.set(
        key,
        json.dumps(value),
        ex=CACHE_TTL
    )