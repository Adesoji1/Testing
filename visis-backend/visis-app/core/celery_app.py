# app/core/celery_app.py

# from celery import Celery
# from app.core.config import settings

# celery_app = Celery(
#     "worker",
#     broker=settings.REDIS_BROKER_URL,
#     backend=settings.REDIS_BACKEND_URL,
#     include=['app.services.celery_tasks']
# )

# celery_app.conf.update(
#     task_serializer="json",
#     accept_content=["json"],
#     result_serializer="json",
#     timezone="UTC",
#     enable_utc=True,
# )
