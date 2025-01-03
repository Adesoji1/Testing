# app/api/endpoints/user/subscriptions.py

# from fastapi import APIRouter, Depends, HTTPException, Request
# from sqlalchemy.orm import Session
# from typing import List
# from app.services.subscription_service import (
#     create_subscription,
#     save_subscription,
#     list_subscriptions,
#     fetch_subscription,
# )
# from app.models.user import User
# from app.schemas.subscription import SubscriptionRequest, SubscriptionResponse
# from app.api.endpoints.user.auth import get_current_user
# from app.database import get_db
# import logging

# logger = logging.getLogger(__name__)

# router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

# @router.post("/create", response_model=SubscriptionResponse)
# async def subscription_create(
#     subscription_request: SubscriptionRequest,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     try:
#         data = create_subscription(
#             email=subscription_request.email,
#             plan_code=subscription_request.plan_code
#         )
#         # Save subscription to database
#         save_subscription(data, current_user.id, db)
#         return data
#     except Exception as e:
#         logger.error(f"Error creating subscription: {e}")
#         raise HTTPException(status_code=400, detail=str(e))

# @router.get("/", response_model=List[SubscriptionResponse])
# async def get_subscriptions(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     subscriptions = list_subscriptions(db, current_user.id)
#     return subscriptions

# @router.get("/{subscription_code}", response_model=SubscriptionResponse)
# async def get_subscription(
#     subscription_code: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     subscription = fetch_subscription(db, subscription_code)
#     if not subscription or subscription.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Subscription not found")
#     return subscription



# # app/api/endpoints/user/subscriptions.py

# from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
# from sqlalchemy.orm import Session
# from typing import List
# from app.services.subscription_service import (
#     create_subscription,
#     save_subscription,
#     list_subscriptions,
#     fetch_subscription,
# )
# from app.models.user import User
# from app.schemas.subscription import SubscriptionInitializeRequest, SubscriptionResponse
# from app.api.endpoints.user.auth import get_current_user
# from app.database import get_db
# import logging

# logger = logging.getLogger(__name__)

# router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

# @router.post("/create", response_model=SubscriptionResponse)
# async def subscription_create(
#     subscription_request: SubscriptionInitializeRequest,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     try:
#         # Asynchronous subscription creation
#         data = await create_subscription(
#             email=subscription_request.email,
#             plan_code=subscription_request.plan_code
#         )
#         # Asynchronous save to database
#         subscription = await save_subscription(data, current_user.id, db)
#         return SubscriptionResponse.from_orm(subscription)
#     except Exception as e:
#         logger.error(f"Error creating subscription: {e}")
#         raise HTTPException(status_code=400, detail=str(e))

# @router.get("/", response_model=List[SubscriptionResponse])
# async def get_subscriptions(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     subscriptions = list_subscriptions(db, current_user.id)
#     return subscriptions

# @router.get("/{subscription_code}", response_model=SubscriptionResponse)
# async def get_subscription(
#     subscription_code: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     subscription = fetch_subscription(db, subscription_code)
#     if not subscription or subscription.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Subscription not found")
#     return SubscriptionResponse.from_orm(subscription)


# from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request, status
# from sqlalchemy.orm import Session
# from typing import List, Optional
# from datetime import datetime

# from app.database import get_db
# from app.models.user import User
# from app.core.security import get_current_user
# from app.schemas.subscription import SubscriptionInitializeRequest, SubscriptionInitializeResponse, SubscriptionResponse
# from app.services.subscription_service import (
#     create_subscription_in_db,
#     list_subscriptions,
#     fetch_subscription,
#     fetch_subscription_from_paystack,
#     create_subscription_on_paystack,
#     list_subscriptions_from_paystack,
#     save_subscription
# )
# from app.utils.paystack_utils import (
#     paystack_initialize_transaction,
#     verify_paystack_signature,
#     paystack_verify_transaction
# )
# from app.models.subscription import Subscription
# from app.core.config import settings
# import logging

# logger = logging.getLogger(__name__)

# router = APIRouter()

# @router.post("/subscriptions/initiate", response_model=SubscriptionInitializeResponse)
# async def initiate_subscription(
#     payload: SubscriptionInitializeRequest,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Initiate a subscription. This will:
#     - Initialize a transaction with Paystack if needed (e.g., for bank_transfer)
#     - Return an authorization_url or instructions depending on the channel
#     - Once payment is completed (via callback), we finalize subscription creation.
#     """
#     reference = f"sub_{int(datetime.utcnow().timestamp())}"
#     channels = ["card", "bank", "ussd", "mobile_money", "qr", "bank_transfer"]  # allowed channels

#     if payload.channel not in channels:
#         raise HTTPException(status_code=400, detail="Unsupported payment channel.")

#     # Initialize transaction on Paystack
#     try:
#         data = await paystack_initialize_transaction(
#             email=payload.email,
#             amount=payload.amount,
#             reference=reference,
#             currency="NGN",
#             metadata=payload.metadata,
#             channels=[payload.channel],
#             callback_url=settings.PAYSTACK_TRANSACTION_CALLBACK_URL
#         )
#         # data should contain authorization_url and reference
#         return SubscriptionInitializeResponse(
#             authorization_url=data["authorization_url"],
#             access_code=data["access_code"],
#             reference=data["reference"]
#         )
#     except Exception as e:
#         logger.error(f"Failed to initialize subscription transaction: {str(e)}")
#         raise HTTPException(status_code=500, detail="Failed to initialize transaction")


# @router.post("/subscriptions/verify")
# async def verify_subscription_payment(
#     reference: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     After user completes payment, front-end or callback can call this endpoint with reference to verify payment.
#     If successful, create subscription on Paystack and save in DB.
#     """
#     transaction_data = await paystack_verify_transaction(reference)
#     if not transaction_data or transaction_data.get("status") != "success":
#         raise HTTPException(status_code=400, detail="Transaction verification failed or payment not successful.")

#     # Extract customer email and plan_code from transaction_data.metadata if needed
#     # For simplicity, assume we know the plan_code from metadata
#     plan_code = transaction_data["metadata"].get("plan_code")
#     if not plan_code:
#         raise HTTPException(status_code=400, detail="Plan code not provided in transaction metadata.")

#     # Create subscription on Paystack using the customer's authorization and plan code
#     # transaction_data["authorization"] may have the authorization_code
#     authorization_code = transaction_data["authorization"]["authorization_code"]
#     customer_code = transaction_data["customer"]["customer_code"]

#     subscription_data = await create_subscription_on_paystack(
#         customer=customer_code,
#         plan=plan_code,
#         authorization=authorization_code
#     )

#     # Save subscription in DB
#     subscription = await save_subscription(subscription_data, current_user.id, db)

#     return {"detail": "Subscription created successfully.", "subscription_code": subscription.subscription_code}


# @router.get("/subscriptions", response_model=List[SubscriptionResponse])
# def get_user_subscriptions(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     List all subscriptions for the current user from the DB.
#     """
#     subs = list_subscriptions(db, current_user.id)
#     return subs


# @router.get("/subscriptions/{subscription_code}", response_model=SubscriptionResponse)
# def get_subscription_details(
#     subscription_code: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Fetch details of a specific subscription from DB.
#     """
#     sub = fetch_subscription(db, subscription_code)
#     if not sub or sub.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Subscription not found")
#     return sub


# @router.post("/subscriptions/{subscription_code}/enable")
# async def enable_subscription(
#     subscription_code: str,
#     token: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Enable a subscription using subscription code and email token.
#     """
#     sub = fetch_subscription(db, subscription_code)
#     if not sub or sub.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Subscription not found")

#     # Call Paystack enable endpoint
#     # Example: POST /subscription/enable with code and token
#     import httpx
#     url = "https://api.paystack.co/subscription/enable"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#         "Content-Type": "application/json",
#     }
#     data = {
#         "code": subscription_code,
#         "token": token
#     }
#     async with httpx.AsyncClient() as client:
#         response = await client.post(url, headers=headers, json=data)
#     if response.status_code == 200 and response.json().get("status"):
#         # Update subscription status in DB if needed
#         sub.status = "active"
#         db.commit()
#         db.refresh(sub)
#         return {"detail": "Subscription enabled successfully."}
#     else:
#         raise HTTPException(status_code=400, detail="Failed to enable subscription.")


# @router.post("/subscriptions/{subscription_code}/disable")
# async def disable_subscription(
#     subscription_code: str,
#     token: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Disable a subscription using subscription code and email token.
#     """
#     sub = fetch_subscription(db, subscription_code)
#     if not sub or sub.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Subscription not found")

#     import httpx
#     url = "https://api.paystack.co/subscription/disable"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#         "Content-Type": "application/json",
#     }
#     data = {
#         "code": subscription_code,
#         "token": token
#     }
#     async with httpx.AsyncClient() as client:
#         response = await client.post(url, headers=headers, json=data)
#     if response.status_code == 200 and response.json().get("status"):
#         sub.status = "disabled"
#         db.commit()
#         db.refresh(sub)
#         return {"detail": "Subscription disabled successfully."}
#     else:
#         raise HTTPException(status_code=400, detail="Failed to disable subscription.")


# @router.get("/subscriptions/{subscription_code}/manage/link")
# async def generate_update_link(
#     subscription_code: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Generate a link for updating the card on a subscription.
#     """
#     sub = fetch_subscription(db, subscription_code)
#     if not sub or sub.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Subscription not found")

#     import httpx
#     url = f"https://api.paystack.co/subscription/{subscription_code}/manage/link"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#     }
#     async with httpx.AsyncClient() as client:
#         response = await client.get(url, headers=headers)
#     if response.status_code == 200 and response.json().get("status"):
#         return {"link": response.json()["data"]["link"]}
#     else:
#         raise HTTPException(status_code=400, detail="Failed to generate update link.")


# @router.post("/subscriptions/{subscription_code}/manage/email")
# async def send_update_link_email(
#     subscription_code: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Send an email to the customer with a link to update their card on the subscription.
#     """
#     sub = fetch_subscription(db, subscription_code)
#     if not sub or sub.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Subscription not found")

#     import httpx
#     url = f"https://api.paystack.co/subscription/{subscription_code}/manage/email"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#     }
#     async with httpx.AsyncClient() as client:
#         response = await client.post(url, headers=headers)
#     if response.status_code == 200 and response.json().get("status"):
#         return {"detail": "Email successfully sent"}
#     else:
#         raise HTTPException(status_code=400, detail="Failed to send email.")


# @router.get("/subscriptions/remote")
# async def list_subscriptions_remote(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     List subscriptions from Paystack directly (if you want to cross-check).
#     """
#     subs = await list_subscriptions_from_paystack()
#     return subs


# from fastapi import APIRouter, Depends, HTTPException, Form
# from sqlalchemy.orm import Session
# from typing import List
# from datetime import datetime
# from app.database import get_db
# from app.models.user import User
# from app.core.security import get_current_user
# from app.schemas.subscription import SubscriptionInitializeRequest, SubscriptionInitializeResponse, SubscriptionResponse
# from app.services.subscription_service import (
#     list_subscriptions,
#     fetch_subscription,
#     fetch_subscription_from_paystack,
#     list_subscriptions_from_paystack,
#     create_subscription_on_paystack,
#     save_subscription
# )
# from app.utils.paystack_utils import paystack_initialize_transaction, paystack_verify_transaction
# import logging
# from app.core.config import settings

# logger = logging.getLogger(__name__)

# router = APIRouter()

# # @router.post("/subscriptions/initiate", response_model=SubscriptionInitializeResponse)
# # async def initiate_subscription(
# #     payload: SubscriptionInitializeRequest,
# #     db: Session = Depends(get_db),
# #     current_user: User = Depends(get_current_user)
# # ):
# #     """
# #     Initiate a subscription by creating a Paystack transaction.
# #     The metadata includes user_id and plan_code so callback can finalize subscription.
# #     """
# #     reference = f"sub_{int(datetime.utcnow().timestamp())}"
# #     channels = ["card", "bank", "ussd", "mobile_money", "qr", "bank_transfer"]

# #     if payload.channel not in channels:
# #         raise HTTPException(status_code=400, detail="Unsupported payment channel.")

# #     # Add metadata
# #     metadata = payload.metadata or {}
# #     metadata["user_id"] = current_user.id
# #     metadata["plan_code"] = payload.plan_code

# #     try:
# #         data = await paystack_initialize_transaction(
# #             email=payload.email,
# #             amount=payload.amount,
# #             reference=reference,
# #             currency="NGN",
# #             metadata=metadata,
# #             channels=[payload.channel]
# #         )
# #         return SubscriptionInitializeResponse(
# #             authorization_url=data["authorization_url"],
# #             access_code=data["access_code"],
# #             reference=data["reference"]
# #         )
# #     except Exception as e:
# #         logger.error(f"Failed to initialize subscription transaction: {str(e)}")
# #         raise HTTPException(status_code=500, detail="Failed to initialize transaction")

# @router.post("/subscriptions/initiate", response_model=SubscriptionInitializeResponse)
# async def initiate_subscription(
#     email: str = Form(...),
#     amount: float = Form(...),
#     plan_code: str = Form(...),
#     channel: str = Form("card"),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Initiate a subscription using form fields.
#     The user selects channel, provides email, amount, and plan_code.

#     We'll add user_id and plan_code to metadata so callback can finalize subscription creation.
#     """
#     metadata = {"user_id": current_user.id, "plan_code": plan_code}

#     try:
#         data = await paystack_initialize_transaction(
#             email=email,
#             amount=amount,
#             reference=f"sub_{int(datetime.utcnow().timestamp())}",
#             currency="NGN",
#             metadata=metadata,
#             channels=[channel]
#         )
#         return SubscriptionInitializeResponse(
#             authorization_url=data["authorization_url"],
#             access_code=data["access_code"],
#             reference=data["reference"]
#         )
#     except Exception as e:
#         logger.error(f"Failed to initialize subscription transaction: {str(e)}")
#         raise HTTPException(status_code=500, detail="Failed to initialize transaction")




# @router.post("/subscriptions/verify")
# async def verify_subscription_payment(
#     reference: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Manually verify a transaction if needed (not always required if callback works).
#     If successful, create subscription.
#     """
#     transaction_data = await paystack_verify_transaction(reference)
#     if not transaction_data or transaction_data["status"] != "success":
#         raise HTTPException(status_code=400, detail="Transaction verification failed or payment not successful.")

#     metadata = transaction_data["metadata"]
#     user_id = metadata.get("user_id")
#     plan_code = metadata.get("plan_code")
#     if user_id != current_user.id:
#         raise HTTPException(status_code=403, detail="You are not the owner of this transaction.")

#     customer_code = transaction_data["customer"]["customer_code"]
#     authorization_code = transaction_data["authorization"]["authorization_code"]

#     subscription_data = await create_subscription_on_paystack(
#         customer=customer_code,
#         plan=plan_code,
#         authorization=authorization_code
#     )

#     sub = await save_subscription(subscription_data, user_id, db)
#     return {"detail": "Subscription created successfully.", "subscription_code": sub.reference}


# # @router.get("/subscriptions", response_model=List[SubscriptionResponse])
# # def get_user_subscriptions(
# #     db: Session = Depends(get_db),
# #     current_user: User = Depends(get_current_user)
# # ):
# #     subs = list_subscriptions(db, current_user.id)
# #     return subs


# @router.get("/subscriptions", response_model=list[SubscriptionResponse])
# def get_user_subscriptions(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     subs = list_subscriptions(db, current_user.id)
#     results = []
#     for s in subs:
#         results.append(SubscriptionResponse(
#             id=s.id,
#             subscription_code=s.subscription_code,
#             plan_code=s.plan_code,
#             amount=s.amount,
#             currency=s.currency,
#             status=s.status,
#             start_date=s.start_date,
#             next_payment_date=s.next_payment_date,
#             subscription_metadata=s.subscription_metadata,
#             customer_email=s.user.email
#         ))
#     return results



# @router.get("/subscriptions/{subscription_code}", response_model=SubscriptionResponse)
# def get_subscription_details(
#     subscription_code: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     sub = fetch_subscription(db, subscription_code)
#     if not sub or sub.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Subscription not found")
#     return sub


# @router.post("/subscriptions/{subscription_code}/enable")
# async def enable_subscription(
#     subscription_code: str,
#     token: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     sub = fetch_subscription(db, subscription_code)
#     if not sub or sub.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Subscription not found")

#     import httpx
#     url = "https://api.paystack.co/subscription/enable"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#         "Content-Type": "application/json",
#     }
#     data = {
#         "code": subscription_code,
#         "token": token
#     }
#     async with httpx.AsyncClient() as client:
#         response = await client.post(url, headers=headers, json=data)
#     if response.status_code == 200 and response.json().get("status"):
#         sub.status = "active"
#         db.commit()
#         db.refresh(sub)
#         return {"detail": "Subscription enabled successfully."}
#     else:
#         raise HTTPException(status_code=400, detail="Failed to enable subscription.")


# @router.post("/subscriptions/{subscription_code}/disable")
# async def disable_subscription(
#     subscription_code: str,
#     token: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     sub = fetch_subscription(db, subscription_code)
#     if not sub or sub.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Subscription not found")

#     import httpx
#     url = "https://api.paystack.co/subscription/disable"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#         "Content-Type": "application/json",
#     }
#     data = {
#         "code": subscription_code,
#         "token": token
#     }
#     async with httpx.AsyncClient() as client:
#         response = await client.post(url, headers=headers, json=data)
#     if response.status_code == 200 and response.json().get("status"):
#         sub.status = "disabled"
#         db.commit()
#         db.refresh(sub)
#         return {"detail": "Subscription disabled successfully."}
#     else:
#         raise HTTPException(status_code=400, detail="Failed to disable subscription.")


# @router.get("/subscriptions/remote")
# async def list_subscriptions_remote(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     subs = await list_subscriptions_from_paystack()
#     return subs


# import json
# from app.services.subscription_service import fetch_subscription, pause_subscription_on_paystack,list_subscriptions,resolve_nigeria_account
# from fastapi import APIRouter, Depends, HTTPException, Form
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.models.user import User
# from app.core.security import get_current_user
# from app.schemas.subscription import SubscriptionInitializeResponse, SubscriptionResponse
# from app.utils.paystack_utils import paystack_initialize_transaction
# from datetime import datetime
# from typing import List
# import logging

# logger = logging.getLogger(__name__)

# router = APIRouter()

# @router.post("/subscriptions/initiate", response_model=SubscriptionInitializeResponse)
# async def initiate_subscription(
#     email: str = Form(...),
#     amount: float = Form(...),
#     plan_code: str = Form(...),
#     channel: str = Form("card"),
#     bank_code: str = Form(None),
#     account_number: str = Form(None),
#     metadata_str: str = Form(None),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Initiate a subscription using form fields.
#     If channel=bank_transfer and bank_code+account_number provided,
#     verify account number first.
#     """
#     # if metadata_str:
#     #     try:
#     #         metadata = json.loads(metadata_str)
#     #     except json.JSONDecodeError:
#     #         raise HTTPException(status_code=400, detail="Invalid JSON format for metadata.")
#     # else:
#     #     metadata_str = {}

#     metadata = {}
#     if metadata_str:
  
#         metadata = json.loads(metadata_str)
#     metadata["user_id"] = current_user.id
#     metadata["plan_code"] = plan_code

#     # If bank_transfer, resolve account
#     if channel == "bank_transfer":
#         if not bank_code or not account_number:
#             raise HTTPException(status_code=400, detail="Bank code and account number required for bank transfer.")
#         try:
#             account_data = await resolve_nigeria_account(account_number, bank_code)
#             # account_data has account_name, confirm if needed
#             logger.info(f"Resolved account: {account_data['account_name']}")
#         except Exception as e:
#             logger.error(f"Failed to resolve account number: {e}")
#             raise HTTPException(status_code=400, detail="Could not resolve account number.")

#     try:
#         data = await paystack_initialize_transaction(
#             email=email,
#             amount=amount,
#             reference=f"sub_{int(datetime.utcnow().timestamp())}",
#             currency="NGN",
#             metadata=metadata,
#             channels=[channel]
#         )
#         return SubscriptionInitializeResponse(
#             authorization_url=data["authorization_url"],
#             access_code=data["access_code"],
#             reference=data["reference"]
#         )
#     except Exception as e:
#         logger.error(f"Failed to initialize subscription transaction: {str(e)}")
#         raise HTTPException(status_code=500, detail="Failed to initialize transaction")


# @router.get("/subscriptions", response_model=List[SubscriptionResponse])
# def get_user_subscriptions(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     subs = list_subscriptions(db, current_user.id)
#     results = []
#     for s in subs:
#         results.append(SubscriptionResponse(
#             id=s.id,
#             subscription_code=s.subscription_code,
#             plan_code=s.plan_code,
#             amount=s.amount,
#             currency=s.currency,
#             status=s.status,
#             start_date=s.start_date,
#             next_payment_date=s.next_payment_date,
#             subscription_metadata=s.subscription_metadata,
#             customer_email=s.user.email
#         ))
#     return results


# @router.get("/subscriptions/{subscription_code}", response_model=SubscriptionResponse)
# def get_subscription_details(
#     subscription_code: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     from app.services.subscription_service import fetch_subscription
#     sub = fetch_subscription(db, subscription_code, current_user.id)
#     if not sub:
#         raise HTTPException(status_code=404, detail="Subscription not found")

#     return SubscriptionResponse(
#         id=sub.id,
#         subscription_code=sub.subscription_code,
#         plan_code=sub.plan_code,
#         amount=sub.amount,
#         currency=sub.currency,
#         status=sub.status,
#         start_date=sub.start_date,
#         next_payment_date=sub.next_payment_date,
#         subscription_metadata=sub.subscription_metadata,
#         customer_email=sub.user.email
#     )

# @router.post("/subscriptions/{subscription_code}/pause")
# async def pause_subscription(
#     subscription_code: str,
#     token: str = Form(...),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
    
#     sub = fetch_subscription(db, subscription_code, current_user.id)
#     if not sub:
#         raise HTTPException(status_code=404, detail="Subscription not found")

#     resp = await pause_subscription_on_paystack(subscription_code, token)
#     if resp.get("status"):
#         sub.status = "paused"
#         db.commit()
#         db.refresh(sub)
#         return {"detail": "Subscription paused successfully"}
#     else:
#         raise HTTPException(status_code=400, detail="Failed to pause subscription")

# @router.post("/subscriptions/{subscription_code}/resume")
# async def resume_subscription(
#     subscription_code: str,
#     token: str = Form(...),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     from app.services.subscription_service import fetch_subscription, resume_subscription_on_paystack
#     sub = fetch_subscription(db, subscription_code, current_user.id)
#     if not sub:
#         raise HTTPException(status_code=404, detail="Subscription not found")

#     resp = await resume_subscription_on_paystack(subscription_code, token)
#     if resp.get("status"):
#         sub.status = "active"
#         db.commit()
#         db.refresh(sub)
#         return {"detail": "Subscription resumed successfully"}
#     else:
#         raise HTTPException(status_code=400, detail="Failed to resume subscription")


# from fastapi import APIRouter, Depends, HTTPException, Form
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.models.user import User
# from app.core.security import get_current_user
# from app.schemas.subscription import SubscriptionInitializeResponse, SubscriptionResponse
# from app.services.subscription_service import (list_subscriptions, fetch_subscription, resolve_nigeria_account)
# from app.utils.paystack_utils import paystack_initialize_transaction
# import json
# import logging
# from datetime import datetime

# logger = logging.getLogger(__name__)

# router = APIRouter()

# @router.post("/subscriptions/initiate", response_model=SubscriptionInitializeResponse)
# async def initiate_subscription(
#     email: str = Form(...),
#     amount: float = Form(...),
#     plan_code: str = Form(...),
#     channel: str = Form("card"),
#     bank_code: str = Form(None),
#     account_number: str = Form(None),
#     metadata_str: str = Form(None),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Initiate a subscription using form fields with metadata.
#     If channel=bank_transfer and bank_code+account_number provided, verify account number first.
#     """
#     if metadata_str:
#         try:
#             metadata = json.loads(metadata_str)
#         except json.JSONDecodeError:
#             raise HTTPException(status_code=400, detail="Invalid JSON format for metadata.")
#     else:
#         metadata = {}

#     # Add required fields to metadata
#     metadata["user_id"] = current_user.id
#     metadata["plan_code"] = plan_code
#     # Example: Add recurring billing
#     metadata.setdefault("custom_filters", {})
#     metadata["custom_filters"]["recurring"] = True
#     # Add custom fields if needed
#     metadata.setdefault("custom_fields", [])
#     metadata["custom_fields"].append({
#         "display_name": "Invoice ID",
#         "variable_name": "invoice_id",
#         "value": 209
#     })
#     # If you want a cancel_action:
#     # metadata["cancel_action"] = "https://your-cancel-url.com"

#     # If bank_transfer, resolve account
#     if channel == "bank_transfer":
#         if not bank_code or not account_number:
#             raise HTTPException(status_code=400, detail="Bank code and account number required for bank transfer.")
#         try:
#             account_data = await resolve_nigeria_account(account_number, bank_code)
#             logger.info(f"Resolved account: {account_data['account_name']}")
#         except Exception as e:
#             logger.error(f"Failed to resolve account number: {e}")
#             raise HTTPException(status_code=400, detail="Could not resolve account number.")

#     try:
#         data = await paystack_initialize_transaction(
#             email=email,
#             amount=amount,
#             reference=f"sub_{int(datetime.utcnow().timestamp())}",
#             currency="NGN",
#             metadata=metadata,
#             channels=[channel]
#         )
#         return SubscriptionInitializeResponse(
#             authorization_url=data["authorization_url"],
#             access_code=data["access_code"],
#             reference=data["reference"]
#         )
#     except Exception as e:
#         logger.error(f"Failed to initialize subscription transaction: {str(e)}")
#         raise HTTPException(status_code=500, detail="Failed to initialize transaction")


# @router.get("/subscriptions", response_model=list[SubscriptionResponse])
# def get_user_subscriptions(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     subs = list_subscriptions(db, current_user.id)
#     results = []
#     for s in subs:
#         results.append(SubscriptionResponse(
#             id=s.id,
#             subscription_code=s.subscription_code,
#             plan_code=s.plan_code,
#             amount=s.amount,
#             currency=s.currency,
#             status=s.status,
#             start_date=s.start_date,
#             next_payment_date=s.next_payment_date,
#             subscription_metadata=s.subscription_metadata,
#             customer_email=s.user.email
#         ))
#     return results

# @router.get("/subscriptions/{subscription_code}", response_model=SubscriptionResponse)
# def get_subscription_details(
#     subscription_code: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     from app.services.subscription_service import fetch_subscription
#     sub = fetch_subscription(db, subscription_code, current_user.id)
#     if not sub:
#         raise HTTPException(status_code=404, detail="Subscription not found")

#     return SubscriptionResponse(
#         id=sub.id,
#         subscription_code=sub.subscription_code,
#         plan_code=sub.plan_code,
#         amount=sub.amount,
#         currency=sub.currency,
#         status=sub.status,
#         start_date=sub.start_date,
#         next_payment_date=sub.next_payment_date,
#         subscription_metadata=sub.subscription_metadata,
#         customer_email=sub.user.email
#     )

# @router.post("/subscriptions/{subscription_code}/pause")
# async def pause_subscription(
#     subscription_code: str,
#     token: str = Form(...),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     from app.services.subscription_service import fetch_subscription, pause_subscription_on_paystack
#     sub = fetch_subscription(db, subscription_code, current_user.id)
#     if not sub:
#         raise HTTPException(status_code=404, detail="Subscription not found")

#     resp = await pause_subscription_on_paystack(subscription_code, token)
#     if resp.get("status"):
#         sub.status = "paused"
#         db.commit()
#         db.refresh(sub)
#         return {"detail": "Subscription paused successfully"}
#     else:
#         raise HTTPException(status_code=400, detail="Failed to pause subscription")

# @router.post("/subscriptions/{subscription_code}/resume")
# async def resume_subscription(
#     subscription_code: str,
#     token: str = Form(...),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     from app.services.subscription_service import fetch_subscription, resume_subscription_on_paystack
#     sub = fetch_subscription(db, subscription_code, current_user.id)
#     if not sub:
#         raise HTTPException(status_code=404, detail="Subscription not found")

#     resp = await resume_subscription_on_paystack(subscription_code, token)
#     if resp.get("status"):
#         sub.status = "active"
#         db.commit()
#         db.refresh(sub)
#         return {"detail": "Subscription resumed successfully"}
#     else:
#         raise HTTPException(status_code=400, detail="Failed to resume subscription")



# app/api/endpoints/subscriptions.py
from fastapi import APIRouter, HTTPException
from app.core.config import settings
import httpx
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/subscriptions/initiate")
async def initiate_subscription(email: str, plan_code: str):
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "email": email,
        "plan": plan_code,
        "metadata": {
            "user_id": "1",  # use actual user_id
            "plan_code": plan_code,
            "custom_filters": {"recurring": "true"},
            "custom_fields": [
                {
                    "display_name": "Invoice ID",
                    "variable_name": "invoice_id",
                    "value": "209"
                }
            ]
        },
        # DO NOT include "amount" if you rely solely on plan’s amount
        # "channels": ["card","bank","ussd"] if you wish to allow multiple channels
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=data)
    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to initialize transaction: {e.response.text}")
        raise HTTPException(status_code=400, detail="Failed to initialize subscription transaction")

    init_data = resp.json()["data"]
    return {"authorization_url": init_data["authorization_url"], "access_code": init_data["access_code"], "reference": init_data["reference"]}

# async def initiate_subscription(email: str, plan_code: str):
#     """
#     Initiate a subscription by including the plan in the transaction initialize request.
#     The user_id can be part of the metadata if you have an authenticated user.
#     """
#     url = "https://api.paystack.co/transaction/initialize"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#         "Content-Type": "application/json",
#     }
#     data = {
#         "email": email,
#         "plan": plan_code,
#         # If you want to enforce the plan amount, you can omit "amount"
#         # Add user_id to metadata if you have it from an authenticated user session:
#         "metadata": {
#             "user_id": "1",  # replace with actual user_id from authentication
#             "plan_code": plan_code,
#             "custom_filters": {"recurring": "true"},
#             "custom_fields": [
#                 {
#                     "display_name": "Invoice ID",
#                     "variable_name": "invoice_id",
#                     "value": "209"
#                 }
#             ]
#         },
#         # Optional: specify channels
#         "channels": ["card", "bank", "ussd"]
#     }

#     async with httpx.AsyncClient() as client:
#         resp = await client.post(url, headers=headers, json=data)
#     try:
#         resp.raise_for_status()
#     except httpx.HTTPStatusError as e:
#         logger.error(f"Failed to initialize transaction: {e.response.text}")
#         raise HTTPException(status_code=400, detail="Failed to initialize subscription transaction")

#     init_data = resp.json()["data"]
#     # init_data includes authorization_url
#     return {"authorization_url": init_data["authorization_url"], "access_code": init_data["access_code"], "reference": init_data["reference"]}
