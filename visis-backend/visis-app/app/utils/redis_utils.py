#app/utils/redis_utils.py

# import redis
# from app.core.config import settings

# redis_client = redis.Redis(
#     host=settings.REDIS_HOST,
#     port=settings.REDIS_PORT,
#     # password=settings.REDIS_PASSWORD,
#     db=settings.REDIS_DB
# )

# def delete_pattern(pattern):
#     """Delete all keys matching the given pattern."""
#     cursor = '0'
#     while cursor != 0:
#         cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=1000)
#         if keys:
#             redis_client.delete(*keys)
#     # First scan
#     cursor, keys = redis_client.scan(cursor=0, match=pattern, count=1000)
#     if keys:
#         redis_client.delete(*keys)
#     while cursor != 0:
#         cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=1000)
#         if keys:
#             redis_client.delete(*keys)


# # app/utils/redis_client.py

import logging
from typing import Optional, List

import redis
from app.core.config import settings

logger = logging.getLogger(__name__)

def get_redis_client():
    try:
        client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            # password=settings.REDIS_PASSWORD,  # Uncomment if you add a password
            decode_responses=True
        )
        # Test the connection
        client.ping()
        logger.info("Connected to Redis successfully.")
        return client
    except redis.exceptions.ConnectionError as e:
        logger.error(f"Redis connection failed: {e}")
        raise

# Initialize Redis client once
redis_client = get_redis_client()


def delete_pattern(pattern: str):
    """
    Delete all keys matching the given pattern.
    """
    logger.info(f"Deleting keys matching pattern: {pattern}")
    try:
        cursor = 0  # Initialize cursor as integer 0
        while True:
            cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=1000)
            logger.debug(f"SCAN returned cursor: {cursor}, keys: {keys}")
            if keys:
                redis_client.delete(*keys)
                logger.debug(f"Deleted keys: {keys}")
            if cursor == 0:
                break
        logger.info(f"All keys matching pattern '{pattern}' have been deleted.")
    except Exception as e:
        logger.error(f"Error deleting keys with pattern '{pattern}': {e}")
        raise


# def delete_pattern(pattern: str):
#     """
#     Delete all keys matching the given pattern.
#     """
#     logger.info(f"Deleting keys matching pattern: {pattern}")
#     try:
#         cursor = 0
#         while True:
#             cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=1000)
#             if keys:
#                 redis_client.delete(*keys)
#                 logger.debug(f"Deleted keys: {keys}")
#             if cursor == '0':
#                 break
#         logger.info(f"All keys matching pattern '{pattern}' have been deleted.")
#     except Exception as e:
#         logger.error(f"Error deleting keys with pattern '{pattern}': {e}")
#         raise

# #app/utils/redis_utils.py
# import logging
# import redis
# import json
# from typing import Any, Optional, List
# from app.core.config import settings

# # Configure logging
# logger = logging.getLogger(__name__)

# def get_redis_client():
#     """
#     Initialize and return a Redis client instance.

#     Returns:
#         redis.Redis: Redis client instance.
#     """
#     try:
#         client = redis.Redis(
#             host=settings.REDIS_HOST,
#             port=settings.REDIS_PORT,
#             db=settings.REDIS_DB,
#             # password=settings.REDIS_PASSWORD,  # Uncomment if a password is required
#             decode_responses=True,
#         )
#         # Test the connection
#         client.ping()
#         logger.info("Connected to Redis successfully.")
#         return client
#     except redis.exceptions.ConnectionError as e:
#         logger.error(f"Redis connection failed: {e}")
#         raise

# # Initialize Redis client once
# redis_client = get_redis_client()

# def cache_set(key: str, value: Any, ex: Optional[int] = None):
#     """
#     Set a value in the Redis cache.

#     Args:
#         key (str): Cache key.
#         value (Any): Value to cache (serialized to JSON).
#         ex (Optional[int]): Expiration time in seconds (optional).
#     """
#     try:
#         redis_client.set(key, json.dumps(value), ex=ex)
#         logger.info(f"Cached key: {key}")
#     except Exception as e:
#         logger.error(f"Failed to cache key {key}: {e}")
#         raise

# def cache_get(key: str) -> Optional[Any]:
#     """
#     Retrieve a value from the Redis cache.

#     Args:
#         key (str): Cache key.

#     Returns:
#         Optional[Any]: The deserialized value or None if the key is not found.
#     """
#     try:
#         value = redis_client.get(key)
#         if value:
#             return json.loads(value)
#         logger.info(f"Key {key} not found in cache.")
#         return None
#     except Exception as e:
#         logger.error(f"Failed to retrieve cache for key {key}: {e}")
#         return None

# def delete_pattern(pattern: str):
#     """
#     Delete all Redis keys matching a given pattern.

#     Args:
#         pattern (str): Pattern to match keys (e.g., "user:*").
#     """
#     logger.info(f"Deleting keys matching pattern: {pattern}")
#     try:
#         cursor = '0'
#         while True:
#             cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=1000)
#             if keys:
#                 redis_client.delete(*keys)
#                 logger.debug(f"Deleted keys: {keys}")
#             if cursor == '0':  # End of scan
#                 break
#         logger.info(f"All keys matching pattern '{pattern}' have been deleted.")
#     except Exception as e:
#         logger.error(f"Error deleting keys with pattern '{pattern}': {e}")
#         raise



# import logging
# import redis
# import json
# from typing import Any, Optional
# from app.core.config import settings

# # Configure logging
# logger = logging.getLogger(__name__)

# def get_redis_client():
#     """
#     Initialize and return a Redis client instance.
#     """
#     try:
#         client = redis.Redis(
#             host=settings.REDIS_HOST,
#             port=settings.REDIS_PORT,
#             db=settings.REDIS_DB,
#             decode_responses=True,
#         )
#         # Test the connection
#         client.ping()
#         logger.info("Connected to Redis successfully.")
#         return client
#     except redis.exceptions.ConnectionError as e:
#         logger.error(f"Redis connection failed: {e}")
#         raise

# # Initialize Redis client once
# redis_client = get_redis_client()

# def cache_set(key: str, value: Any, ex: Optional[int] = None):
#     """
#     Set a value in the Redis cache.
#     """
#     try:
#         redis_client.set(key, json.dumps(value), ex=ex)
#         logger.info(f"Cached key: {key}")
#     except Exception as e:
#         logger.error(f"Failed to cache key {key}: {e}")
#         raise

# def cache_get(key: str) -> Optional[Any]:
#     """
#     Retrieve a value from the Redis cache.
#     """
#     try:
#         value = redis_client.get(key)
#         if value:
#             return json.loads(value)
#         logger.info(f"Key {key} not found in cache.")
#         return None
#     except Exception as e:
#         logger.error(f"Failed to retrieve cache for key {key}: {e}")
#         return None

# def delete_pattern(pattern: str):
#     """
#     Delete all Redis keys matching a given pattern.
#     """
#     logger.info(f"Deleting keys matching pattern: {pattern}")
#     try:
#         cursor = '0'
#         while True:
#             cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=1000)
#             if keys:
#                 redis_client.delete(*keys)
#                 logger.debug(f"Deleted keys: {keys}")
#             if cursor == '0':  # End of scan
#                 break
#         logger.info(f"All keys matching pattern '{pattern}' have been deleted.")
#     except Exception as e:
#         logger.error(f"Error deleting keys with pattern '{pattern}': {e}")
#         raise
