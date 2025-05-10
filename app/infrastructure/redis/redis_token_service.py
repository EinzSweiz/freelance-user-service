from redis.asyncio import Redis
from datetime import datetime, timezone


class RedisTokenBlacklist:
    def __init__(self, redis_host: str = "redis", redis_port: int = 6379, redis_db: int = 0):
        self.redis = Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

    async def blacklist_token(self, jti: str, exp_timestamp: int) -> None:
        now_ts = int(datetime.now(tz=timezone.utc).timestamp())
        ttl = exp_timestamp - now_ts
        if ttl > 0:
            await self.redis.setex(jti, ttl, "blacklisted")

    async def is_token_blacklisted(self, jti: str) -> bool:
        return await self.redis.exists(jti) == 1
