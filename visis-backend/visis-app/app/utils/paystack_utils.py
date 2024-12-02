# app/utils/paystack_utils.py

import hmac
import hashlib
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def verify_paystack_signature(request):
    signature = request.headers.get('x-paystack-signature', '')
    body = await request.body()
    computed_signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
        msg=body,
        digestmod=hashlib.sha512
    ).hexdigest()
    is_valid = hmac.compare_digest(computed_signature, signature)
    if not is_valid:
        logger.warning("Invalid Paystack signature")
    return is_valid
