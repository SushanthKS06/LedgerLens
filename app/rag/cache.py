import os
import json
import redis.asyncio as redis
from typing import Optional, Dict, Any

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Set up Redis client pooling
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
except Exception as e:
    redis_client = None
    print(f"Warning: Redis failed to initialize. {str(e)}")

async def get_cached(key: str) -> Optional[Dict[str, Any]]:
    if not redis_client:
        return None
    try:
        val = await redis_client.get(key)
        if val:
            return json.loads(val)
    except Exception:
        pass
    return None

async def set_cached(key: str, value: Dict[str, Any], expire: int = 3600):
    if not redis_client:
        return
    try:
        await redis_client.set(key, json.dumps(value), ex=expire)
    except Exception:
        pass
