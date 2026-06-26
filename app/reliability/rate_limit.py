import os
from fastapi import Request, HTTPException
from redis.asyncio import Redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

redis = None

async def init_redis():
    global redis
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis = Redis.from_url(redis_url)
    await FastAPILimiter.init(redis)

def limiter(times: int, seconds: int):
    return RateLimiter(times=times, seconds=seconds)