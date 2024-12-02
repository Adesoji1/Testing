#app/utils/redis_utils.py
# import redis
# from app.core.config import settings

# redis_client = redis.StrictRedis(
#     host=settings.REDIS_HOST,
#     port=settings.REDIS_PORT,
#     db=settings.REDIS_DB,
#     decode_responses=True  # Ensures string responses
# )

# def delete_pattern(pattern: str):
#     """
#     Delete all Redis keys matching the given pattern.
#     """
#     keys = redis_client.keys(pattern)
#     if keys:
#         redis_client.delete(*keys)

import redis
from app.core.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    # password=settings.REDIS_PASSWORD,
    db=settings.REDIS_DB
)

def delete_pattern(pattern):
    """Delete all keys matching the given pattern."""
    cursor = '0'
    while cursor != 0:
        cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=1000)
        if keys:
            redis_client.delete(*keys)
    # First scan
    cursor, keys = redis_client.scan(cursor=0, match=pattern, count=1000)
    if keys:
        redis_client.delete(*keys)
    while cursor != 0:
        cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=1000)
        if keys:
            redis_client.delete(*keys)

