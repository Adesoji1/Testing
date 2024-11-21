# import redis

# r = redis.Redis(host="127.0.0.1", port=6380, db=0)
# try:
#     r.ping()
#     print("Redis connection successful!")
# except Exception as e:
#     print(f"Redis connection failed: {e}")

from fastapi import APIRouter
import logging
import redis

# Set up logging
logger = logging.getLogger(__name__)

# Define the router
router = APIRouter()

@router.get("/health")
async def health_check():
    try:
        # Test Redis connection
        r = redis.Redis(host="127.0.0.1", port=6380, db=0)
        redis_response = r.ping()
        if not redis_response:
            raise Exception("Redis is not responding.")
        logger.info("Redis connection successful.")

        # Test Celery worker
        from app.services.celery_tasks import celery_app
        celery_response = celery_app.control.ping(timeout=1)
        logger.info(f"Celery response: {celery_response}")

        return {
            "status": "healthy",
            "redis": "connected",
            "celery": celery_response
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}
