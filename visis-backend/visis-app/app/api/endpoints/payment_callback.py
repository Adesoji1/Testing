# from fastapi import APIRouter, Depends, HTTPException, Request
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.utils.paystack_utils import verify_paystack_signature, paystack_verify_transaction
# from app.services.subscription_service import create_subscription_on_paystack, save_subscription, fetch_subscription
# from app.models.user import User
# from typing import Optional
# import logging
# import httpx 

# logger = logging.getLogger(__name__)

# router = APIRouter()
# @router.post("/payment/callback")
# async def paystack_callback(request: Request, db: Session = Depends(get_db)):
#     if not await verify_paystack_signature(request):
#         raise HTTPException(status_code=400, detail="Invalid signature")

#     body = await request.json()
#     event = body.get("event")
#     data = body.get("data") 
     

    

#     if event == "charge.success":
#         reference = data.get("reference")
#         transaction_data = await paystack_verify_transaction(reference)
#         if transaction_data and transaction_data["status"] == "success":
#             metadata = transaction_data.get("metadata", {})
#             user_id = metadata.get("user_id")
#             plan_code = metadata.get("plan_code")

#             if not user_id or not plan_code:
#                 logger.error("Missing user_id or plan_code in transaction metadata.")
#                 return {"status": "ok", "message": "User id or plan code missing."}

#             customer_code = transaction_data["customer"]["customer_code"]
#             # Ensure customer_code is valid and from a successful previous transaction
#             try:
#                 subscription_data = await create_subscription_on_paystack(
#                     customer=customer_code,
#                     plan=plan_code
#                 )
#             except httpx.HTTPStatusError as e:
#                 # If we get here, Paystack returned a 400 or similar error. 
#                 # Check logs for the exact error message Paystack returned.
#                 raise HTTPException(status_code=400, detail="Failed to create subscription on Paystack")

#             sub = await save_subscription(subscription_data, user_id, db)
#             logger.info(f"Subscription {sub.subscription_code} created/updated via callback.")

#     return {"status": "ok"}

# # @router.post("/payment/callback")
# # async def paystack_callback(request: Request, db: Session = Depends(get_db)):
# #     # Verify paystack signature
# #     if not await verify_paystack_signature(request):
# #         raise HTTPException(status_code=400, detail="Invalid signature")

# #     body = await request.json()
# #     event = body.get("event")
# #     data = body.get("data")

# #     # For subscription creation, the event we're most interested in is "charge.success"
# #     # which means a payment was successful.
# #     if event == "charge.success":
# #         reference = data.get("reference")
# #         transaction_data = await paystack_verify_transaction(reference)
# #         if transaction_data and transaction_data["status"] == "success":
# #             # Extract metadata that should have user_id, plan_code, etc.
# #             metadata = transaction_data.get("metadata", {})
# #             user_id = metadata.get("user_id")
# #             plan_code = metadata.get("plan_code")
# #             customer_code = transaction_data["customer"]["customer_code"]
# #             authorization_code = transaction_data["authorization"]["authorization_code"]

# #             if not user_id or not plan_code:
# #                 logger.error("Missing user_id or plan_code in transaction metadata.")
# #                 return {"status": "ok", "message": "User id or plan code missing."}

# #             # Create subscription on Paystack
# #             subscription_data = await create_subscription_on_paystack(
# #                 customer=customer_code,
# #                 plan=plan_code,
# #                 authorization=authorization_code
# #             )

# #             # Save subscription in DB
# #             sub = await save_subscription(subscription_data, user_id, db)
# #             logger.info(f"Subscription {sub.reference} created/updated via callback.")

# #     return {"status": "ok"}



# app/api/endpoints/payment_callback.py
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.paystack_utils import verify_paystack_signature, paystack_verify_transaction
from app.models.subscription import Subscription
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def sanitize_none(obj):
    """Recursively convert None values to empty strings in a dict."""
    if isinstance(obj, dict):
        return {k: sanitize_none(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_none(item) for item in obj]
    elif obj is None:
        return ""
    else:
        return obj

@router.post("/payment/callback")
async def paystack_callback(request: Request, db: Session = Depends(get_db)):
    if not await verify_paystack_signature(request):
        raise HTTPException(status_code=400, detail="Invalid signature")

    body = await request.json()
    event = body.get("event")
    data = body.get("data")

    if event == "charge.success":
        reference = data.get("reference")
        transaction_data = await paystack_verify_transaction(reference)
        if transaction_data and transaction_data["status"] == "success":
            metadata = transaction_data.get("metadata", {})
            user_id = metadata.get("user_id")
            plan_code = metadata.get("plan_code")

            if not user_id or not plan_code:
                logger.error("Missing user_id or plan_code in transaction metadata.")
                return {"status": "ok", "message": "User id or plan code missing."}

            # Since we included plan in initialization, subscription is auto-created by Paystack.
            # Just save the data
            customer_code = transaction_data["customer"]["customer_code"]
            amount_naira = transaction_data["amount"] / 100.0
            currency = transaction_data["currency"]
            status = transaction_data["status"]  # "success"

            # Sanitize the transaction_data (convert None -> "")
            sanitized_data = sanitize_none({"data": transaction_data})

            sub = Subscription(
                subscription_code="",  # If you want, you can call /subscription endpoint to get code
                user_id=int(user_id),
                plan_code=plan_code,
                customer_code=customer_code,
                amount=amount_naira,
                currency=currency,
                status=status,
                next_payment_date=None, # You can later update this by querying Paystack subscriptions
                transaction_data=sanitized_data["data"]
            )
            db.add(sub)
            db.commit()
            db.refresh(sub)

            logger.info(f"Subscription for user {user_id} on plan {plan_code} saved successfully.")
            return {"status": "ok", "message": "Subscription created successfully."}

    return {"status": "ok"}
