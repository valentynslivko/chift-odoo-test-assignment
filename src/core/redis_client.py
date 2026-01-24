import logging
from typing import Optional

import redis.asyncio as redis
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError as RedisConnError
from redis.exceptions import TimeoutError as RedisTimeoutError

from src.core.settings import get_settings
from src.utils.exceptions import RedisConnectionError

settings = get_settings()
logger = logging.getLogger(__name__)


class AsyncRedisClient:
    """
    A reusable asynchronous Redis client class that manages its own
    connection pool.
    """

    retry_strategy = Retry(ExponentialBackoff(), 3)

    def __init__(self):
        """
        Initializes the client with connection details and creates a
        connection pool.
        """
        self.redis_url = settings.REDIS_CACHE_URI
        self.pool = None
        self.client = None

    async def connect(self):
        """
        Establishes the connection pool and gets a client.
        This method should be called before performing any operations.
        """
        if not self.pool:
            try:
                self.pool = redis.ConnectionPool.from_url(
                    self.redis_url,
                    decode_responses=True,
                    health_check_interval=30,  # Pings the server if connection was idle > 30s
                    socket_connect_timeout=5,  # Prevents hanging on initial connection
                    retry_on_timeout=True,
                )
                self.client = redis.Redis(
                    connection_pool=self.pool,
                    retry=self.retry_strategy,
                    retry_on_error=[RedisConnError, RedisTimeoutError],
                )

                await self.client.ping()
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self.pool = None
                self.client = None
                raise RedisConnectionError(f"Failed to connect to Redis: {e}")

    async def disconnect(self):
        """
        Closes the client and the connection pool gracefully.
        """
        if self.client:
            await self.client.aclose()
        if self.pool:
            await self.pool.aclose()

    async def reconnect(self):
        """
        Force a reconnection to the Redis server.
        """
        logger.debug("Reconnecting to Redis...")
        await self.disconnect()
        await self.connect()

    async def set_value(
        self, key: str, value: str | int, ttl_seconds: Optional[int] = None
    ):
        """
        Asynchronously sets a key-value pair in Redis.

        Args:
            key (str): The key to set.
            value (str): The value to associate with the key.
            expire (int, optional): Expiration time in seconds. Defaults to None.
        """
        if not self.client:
            raise RedisConnectionError("Client is not connected. Call 'connect' first.")
        try:
            await self.client.set(key, value, ex=ttl_seconds)
        except ConnectionError:
            logger.error("Redis connection error. Attempting to reconnect...")
            await self.client.set(key, value, ex=ttl_seconds)
        except Exception as e:
            logger.debug(f"Error setting value for key '{key}': {e}")
            raise

        logger.debug(
            f"Set '{key}' to '{value}'"
            + (f" with {ttl_seconds}s expiry." if ttl_seconds else ".")
        )

    async def get_value(self, key: str):
        """
        Asynchronously retrieves the value for a given key from Redis.

        Args:
            key (str): The key to retrieve.

        Returns:
            The value associated with the key, or None if the key does not exist.
        """
        if not self.client:
            raise RedisConnectionError("Client is not connected. Call 'connect' first.")
        try:
            value = await self.client.get(key)
        except ConnectionError:
            logger.error("Redis connection error. Attempting to reconnect...")
            value = await self.client.get(key)
        except Exception as e:
            logger.error(f"Error getting value for key '{key}': {e}")
            raise

        # logger.debug(f"Retrieved '{value}' for key '{key}'.")
        return value

    async def del_value(self, key: str):
        if not self.client:
            raise RedisConnectionError("Client is not connected. Call 'connect' first.")
        try:
            await self.client.delete(key)
        except ConnectionError:
            logger.error("Redis connection error. Attempting to reconnect...")
            await self.client.delete(key)
        except Exception as e:
            logger.error(f"Error getting value for key '{key}': {e}")
            raise

        logger.debug(f"Removed key '{key}'.")
        return

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
