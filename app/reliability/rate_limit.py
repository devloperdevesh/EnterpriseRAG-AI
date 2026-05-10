from fastapi import Request, HTTPException
from redis.asyncio import Redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

redis = None

async def init_redis():
    global redis
    redis = Redis(host="localhost", port=6379, db=0)
    await FastAPILimiter.init(redis)

def limiter(times: int, seconds: int):
    return RateLimiter(times=times, seconds=seconds)