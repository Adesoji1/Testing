# test_config.py
from app.core.config import settings

print("RATE_LIMIT:", settings.RATE_LIMIT)
print("PAYSTACK_SECRET_KEY:", settings.PAYSTACK_SECRET_KEY)
