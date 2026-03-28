
import json
from typing import Any, Optional, Union, AsyncIterator

# Redis disabled - imports commented out to prevent any Redis usage
# import redis.asyncio as redis
# from redis.asyncio.connection import ConnectionPool

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Minimal no-op async client to safely satisfy imports when Redis is disabled
class _DummyAsyncClient:
    async def ping(self) -> bool:
        return False

    async def get(self, key: str):
        return None

    async def set(self, key: str, value):
        return True

    async def setex(self, key: str, ttl: int, value):
        return True

    async def delete(self, *keys: str) -> int:
        return 0

    async def exists(self, key: str) -> int:
        return 0

    async def expire(self, key: str, ttl: int) -> bool:
        return False

    async def ttl(self, key: str) -> int:
        return -1

    async def incr(self, key: str) -> int:
        return 0

    async def decr(self, key: str) -> int:
        return 0

    async def sadd(self, key: str, *values: str) -> int:
        return 0

    async def sismember(self, key: str, value: str) -> bool:
        return False

    async def smembers(self, key: str) -> set:
        return set()

    async def srem(self, key: str, *values: str) -> int:
        return 0

    async def hget(self, name: str, key: str):
        return None

    async def hset(self, name: str, key: str, value: str) -> int:
        return 0

    async def hdel(self, name: str, *keys: str) -> int:
        return 0

    async def hgetall(self, name: str) -> dict:
        return {}

    async def keys(self, pattern: str) -> list:
        return []

    async def scan_iter(self, match: Optional[str] = None) -> AsyncIterator[str]:
        if False:
            yield ""
        return


class RedisClient:

    def __init__(self):
        self._client: Optional[_DummyAsyncClient] = None

    async def connect(self) -> None:
        logger.info("Redis support disabled - skipping connect")
        self._client = _DummyAsyncClient()

    async def disconnect(self) -> None:
        logger.info("Redis support disabled - nothing to disconnect")
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = _DummyAsyncClient()
        return self._client

    async def ping(self) -> bool:
        try:
            return await self.client.ping()
        except Exception:
            return False

    async def get(self, key: str) -> Optional[str]:
        return await self.client.get(key)

    async def get_json(self, key: str) -> Optional[Any]:
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(self, key: str, value: Union[str, int, float], ttl: Optional[int] = None) -> bool:
        return True

    async def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        return True

    async def delete(self, *keys: str) -> int:
        return 0

    async def exists(self, key: str) -> bool:
        return False

    async def expire(self, key: str, ttl: int) -> bool:
        return False

    async def ttl(self, key: str) -> int:
        return -1

    async def incr(self, key: str) -> int:
        return 0

    async def decr(self, key: str) -> int:
        return 0

    async def sadd(self, key: str, *values: str) -> int:
        return 0

    async def sismember(self, key: str, value: str) -> bool:
        return False

    async def smembers(self, key: str) -> set:
        return set()

    async def srem(self, key: str, *values: str) -> int:
        return 0

    async def hget(self, name: str, key: str) -> Optional[str]:
        return None

    async def hset(self, name: str, key: str, value: str) -> int:
        return 0

    async def hdel(self, name: str, *keys: str) -> int:
        return 0

    async def hgetall(self, name: str) -> dict:
        return {}

    async def keys(self, pattern: str) -> list:
        return []

    async def blacklist_token(self, jti: str, ttl: int) -> bool:
        return True

    async def is_token_blacklisted(self, jti: str) -> bool:
        return False

    async def cache_user_permissions(self, user_id: str, tenant_id: str, permissions: list, ttl: int = 300) -> bool:
        return True

    async def get_cached_permissions(self, user_id: str, tenant_id: str) -> Optional[list]:
        return None

    async def invalidate_user_permissions(self, user_id: str, tenant_id: Optional[str] = None) -> int:
        return 0


redis_client = RedisClient()


def get_redis_sync():
    class _DummySync:
        def ping(self):
            return False

        def get(self, key: str):
            return None

        def set(self, key: str, value):
            return True

        def setex(self, key: str, ttl: int, value):
            return True

        def delete(self, *keys: str) -> int:
            return 0

        def exists(self, key: str) -> int:
            return 0

        def expire(self, key: str, ttl: int) -> bool:
            return False

        def ttl(self, key: str) -> int:
            return -1

    return _DummySync()


async def get_redis_async():
    return redis_client.client


async def get_redis():
    return redis_client.client


async def get_redis_client() -> RedisClient:
    return redis_client

    async def disconnect(self) -> None:
        if self._client:
            await self._client.close()
            self._client = None
        if self._pool:
            await self._pool.disconnect()
            self._pool = None
        logger.info("Redis connection closed")

    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        return self._client

    async def ping(self) -> bool:
        try:
            if self._client:
                return await self._client.ping()
            return False
        except Exception:
            return False

    async def get(self, key: str) -> Optional[str]:
        return await self.client.get(key)

    async def get_json(self, key: str) -> Optional[Any]:
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(self, key: str, value: Union[str, int, float], ttl: Optional[int] = None) -> bool:
        if ttl:
            return await self.client.setex(key, ttl, value)
        return await self.client.set(key, value)

    async def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        serialized = json.dumps(value, default=str)
        return await self.set(key, serialized, ttl)

    async def delete(self, *keys: str) -> int:
        if not keys:
            return 0
        return await self.client.delete(*keys)

    async def exists(self, key: str) -> bool:
        return await self.client.exists(key) > 0

    async def expire(self, key: str, ttl: int) -> bool:
        return await self.client.expire(key, ttl)

    async def ttl(self, key: str) -> int:
        return await self.client.ttl(key)

    async def incr(self, key: str) -> int:
        return await self.client.incr(key)

    async def decr(self, key: str) -> int:
        return await self.client.decr(key)

    async def sadd(self, key: str, *values: str) -> int:
        return await self.client.sadd(key, *values)

    async def sismember(self, key: str, value: str) -> bool:
        return await self.client.sismember(key, value)

    async def smembers(self, key: str) -> set:
        return await self.client.smembers(key)

    async def srem(self, key: str, *values: str) -> int:
        return await self.client.srem(key, *values)

    async def hget(self, name: str, key: str) -> Optional[str]:
        return await self.client.hget(name, key)

    async def hset(self, name: str, key: str, value: str) -> int:
        return await self.client.hset(name, key, value)

    async def hdel(self, name: str, *keys: str) -> int:
        return await self.client.hdel(name, *keys)

    async def hgetall(self, name: str) -> dict:
        return await self.client.hgetall(name)

    async def keys(self, pattern: str) -> list:
        return await self.client.keys(pattern)

    async def blacklist_token(self, jti: str, ttl: int) -> bool:
        key = f"token:blacklist:{jti}"
        return await self.set(key, "revoked", ttl)

    async def is_token_blacklisted(self, jti: str) -> bool:
        key = f"token:blacklist:{jti}"
        return await self.exists(key)

    async def cache_user_permissions(self, user_id: str, tenant_id: str, permissions: list, ttl: int = 300) -> bool:
        key = f"user:{user_id}:permissions:{tenant_id}"
        return await self.set_json(key, permissions, ttl)

    async def get_cached_permissions(self, user_id: str, tenant_id: str) -> Optional[list]:
        key = f"user:{user_id}:permissions:{tenant_id}"
        return await self.get_json(key)

    async def invalidate_user_permissions(self, user_id: str, tenant_id: Optional[str] = None) -> int:
        if tenant_id:
            key = f"user:{user_id}:permissions:{tenant_id}"
            return await self.delete(key)
        else:
            pattern = f"user:{user_id}:permissions:*"
            keys = []
            async for key in self.client.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                return await self.delete(*keys)
            return 0


redis_client = RedisClient()


def get_redis_sync():
    class _DummySync:
        def ping(self):
            return False

        def get(self, key: str):
            return None

        def set(self, key: str, value):
            return True

        def setex(self, key: str, ttl: int, value):
            return True

        def delete(self, *keys: str) -> int:
            return 0

        def exists(self, key: str) -> int:
            return 0

        def expire(self, key: str, ttl: int) -> bool:
            return False

        def ttl(self, key: str) -> int:
            return -1

    return _DummySync()


async def get_redis_async():
    if redis_client._client is None:
        await redis_client.connect()
    return redis_client.client


async def get_redis():
    if redis_client._client is None:
        await redis_client.connect()
    return redis_client.client


async def get_redis_client() -> RedisClient:
    if redis_client._client is None:
        await redis_client.connect()
    return redis_client
