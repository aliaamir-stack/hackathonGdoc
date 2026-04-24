import asyncio
from typing import Any, Dict, Optional

from redis.asyncio import Redis
from supabase import Client, create_client

from config import get_settings

settings = get_settings()

anon_client: Optional[Client] = None
service_client: Optional[Client] = None
redis_client: Optional[Redis] = None


def get_anon_client() -> Client:
    global anon_client
    if anon_client is None:
        anon_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    return anon_client


def get_service_client() -> Client:
    global service_client
    if service_client is None:
        service_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    return service_client


async def get_redis() -> Redis:
    global redis_client
    if redis_client is None:
        redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client


async def run_supabase(method, *args, **kwargs) -> Dict[str, Any]:
    return await asyncio.to_thread(method, *args, **kwargs)
