#app/services/subscription_service.py

import requests
from app.core.config import settings
from app.models.subscription import Subscription
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

def create_subscription(email: str, plan_code: str):
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "email": email,
        "plan": plan_code,
        "callback_url": settings.PAYSTACK_CALLBACK_URL,
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        logger.error(f"Paystack subscription initialization failed: {response.text}")
        raise Exception(f"Paystack subscription initialization failed: {response.text}")
    return response.json()["data"]

def save_subscription(data, user_id, db: Session):
    subscription = Subscription(
        subscription_id=str(data['id']),
        subscription_code=data['subscription_code'],
        email_token=data['email_token'],
        plan_code=data['plan'],
        amount=data['amount'] / 100,
        currency='NGN',  # Adjust as necessary
        status=data['status'],
        next_payment_date=data.get('next_payment_date'),
        user_id=user_id
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription

def list_subscriptions(db: Session, user_id: int):
    return db.query(Subscription).filter(Subscription.user_id == user_id).all()

def fetch_subscription(db: Session, subscription_code: str):
    return db.query(Subscription).filter(Subscription.subscription_code == subscription_code).first()


def fetch_subscription_from_paystack(subscription_code: str):
    url = f"https://api.paystack.co/subscription/{subscription_code}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        logger.error(f"Failed to fetch subscription: {response.text}")
        return None

def list_subscriptions_from_paystack():
    url = "https://api.paystack.co/subscription"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        logger.error(f"Failed to list subscriptions: {response.text}")
        return []


# app/services/subscription_service.py
# import httpx
# from app.core.config import settings
# from sqlalchemy.orm import Session
# from app.models.subscription import Subscription
# from app.models.user import User
# from typing import Optional, Dict, Any, List
# from datetime import datetime
# import logging
# from app.utils.paystack_utils import resolve_account_number

# logger = logging.getLogger(__name__)

# async def create_subscription_on_paystack(customer: str, plan: str, authorization: Optional[str] = None, start_date: Optional[str] = None) -> dict:
#     """
#     Create a subscription on Paystack.
#     """
#     url = "https://api.paystack.co/subscription"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#         "Content-Type": "application/json",
#     }
#     data = {
#         "customer": customer,
#         "plan": plan,
#     }
#     if authorization:
#         data["authorization"] = authorization
#     if start_date:
#         data["start_date"] = start_date

#     async with httpx.AsyncClient() as client:
#         response = await client.post(url, headers=headers, json=data)
#     response.raise_for_status()
#     return response.json()["data"]

# async def save_subscription(data: dict, user_id: int, db: Session) -> Subscription:
#     subscription_code = data["subscription_code"]
#     sub = db.query(Subscription).filter(Subscription.subscription_code == subscription_code, Subscription.user_id == user_id).first()

#     plan_info = data["plan"]
#     plan_code = plan_info.get("plan_code")
#     amount_kobo = data.get("amount", 0)
#     amount_naira = amount_kobo/100.0 if amount_kobo else 0.0
#     start_timestamp = data.get("start")
#     if start_timestamp:
#         start_date = datetime.utcfromtimestamp(start_timestamp)
#     else:
#         start_date = datetime.utcnow()

#     next_payment_str = data.get("next_payment_date")
#     next_payment_date = None
#     if next_payment_str:
#         next_payment_date = datetime.fromisoformat(next_payment_str.replace("Z", "+00:00"))

#     if sub:
#         sub.status = data.get("status", sub.status)
#         sub.next_payment_date = next_payment_date
#         sub.subscription_metadata = data.get("metadata", sub.subscription_metadata)
#     else:
#         sub = Subscription(
#             subscription_code=subscription_code,
#             plan_code=plan_code,
#             amount=amount_naira,
#             currency=plan_info.get("currency", "NGN"),
#             status=data.get("status", "active"),
#             start_date=start_date,
#             next_payment_date=next_payment_date,
#             subscription_metadata=data.get("metadata"),
#             user_id=user_id
#         )
#         db.add(sub)

#     db.commit()
#     db.refresh(sub)
#     return sub

# def list_subscriptions(db: Session, user_id: int) -> List[Subscription]:
#     return db.query(Subscription).filter(Subscription.user_id == user_id).all()

# def fetch_subscription(db: Session, subscription_code: str, user_id: int) -> Optional[Subscription]:
#     return db.query(Subscription).filter(Subscription.subscription_code == subscription_code, Subscription.user_id == user_id).first()

# async def pause_subscription_on_paystack(subscription_code: str, token: str):
#     url = "https://api.paystack.co/subscription/disable"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#         "Content-Type": "application/json"
#     }
#     data = {"code": subscription_code, "token": token}
#     async with httpx.AsyncClient() as client:
#         resp = await client.post(url, headers=headers, json=data)
#     resp.raise_for_status()
#     return resp.json()

# async def resume_subscription_on_paystack(subscription_code: str, token: str):
#     url = "https://api.paystack.co/subscription/enable"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#         "Content-Type": "application/json"
#     }
#     data = {"code": subscription_code, "token": token}
#     async with httpx.AsyncClient() as client:
#         resp = await client.post(url, headers=headers, json=data)
#     resp.raise_for_status()
#     return resp.json()

# async def fetch_subscription_from_paystack(subscription_code: str) -> Optional[dict]:
#     url = f"https://api.paystack.co/subscription/{subscription_code}"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#     }
#     async with httpx.AsyncClient() as client:
#         response = await client.get(url, headers=headers)
#     if response.status_code == 200:
#         return response.json()["data"]
#     else:
#         logger.error(f"Failed to fetch subscription from paystack: {response.text}")
#         return None

# async def resolve_nigeria_account(account_number: str, bank_code: str):
  
#     return await resolve_account_number(account_number, bank_code)

import httpx
from app.core.config import settings
from sqlalchemy.orm import Session
from app.models.subscription import Subscription
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# async def create_subscription_on_paystack(customer: str, plan: str) -> dict:
#     """
#     Create a subscription on Paystack using customer code and plan code only.
#     """
#     url = "https://api.paystack.co/subscription"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#         "Content-Type": "application/json",
#     }
#     data = {
#         "customer": customer,
#         "plan": plan
#     }

#     async with httpx.AsyncClient() as client:
#         response = await client.post(url, headers=headers, json=data)
#     response.raise_for_status()
#     return response.json()["data"]

import httpx
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def create_subscription_on_paystack(customer: str, plan: str) -> dict:
    """
    Create a subscription on Paystack using customer code (e.g. CUS_xxx) and plan code (PLN_xxx).
    """
    url = "https://api.paystack.co/subscription"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "customer": customer,
        "plan": plan
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        # Log the error response to understand what Paystack returned
        logger.error(f"Paystack subscription creation failed: {e.response.text}")
        raise
    return response.json()["data"]


async def save_subscription(data: dict, user_id: int, db: Session) -> Subscription:
    subscription_code = data["subscription_code"]
    sub = db.query(Subscription).filter(Subscription.subscription_code == subscription_code, Subscription.user_id == user_id).first()

    plan_info = data["plan"]
    plan_code = plan_info.get("plan_code")
    amount_kobo = data.get("amount", 0)
    amount_naira = amount_kobo / 100.0 if amount_kobo else 0.0
    start_timestamp = data.get("start")
    if start_timestamp:
        start_date = datetime.utcfromtimestamp(start_timestamp)
    else:
        start_date = datetime.utcnow()

    next_payment_str = data.get("next_payment_date")
    next_payment_date = None
    if next_payment_str:
        next_payment_date = datetime.fromisoformat(next_payment_str.replace("Z", "+00:00"))

    if sub:
        sub.status = data.get("status", sub.status)
        sub.next_payment_date = next_payment_date
        sub.subscription_metadata = data.get("metadata", sub.subscription_metadata)
    else:
        sub = Subscription(
            subscription_code=subscription_code,
            plan_code=plan_code,
            amount=amount_naira,
            currency=plan_info.get("currency", "NGN"),
            status=data.get("status", "active"),
            start_date=start_date,
            next_payment_date=next_payment_date,
            subscription_metadata=data.get("metadata"),
            user_id=user_id
        )
        db.add(sub)

    db.commit()
    db.refresh(sub)
    return sub

def list_subscriptions(db: Session, user_id: int) -> List[Subscription]:
    return db.query(Subscription).filter(Subscription.user_id == user_id).all()

def fetch_subscription(db: Session, subscription_code: str, user_id: int) -> Optional[Subscription]:
    return db.query(Subscription).filter(Subscription.subscription_code == subscription_code, Subscription.user_id == user_id).first()

async def pause_subscription_on_paystack(subscription_code: str, token: str):
    url = "https://api.paystack.co/subscription/disable"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {"code": subscription_code, "token": token}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=data)
    resp.raise_for_status()
    return resp.json()

async def resume_subscription_on_paystack(subscription_code: str, token: str):
    url = "https://api.paystack.co/subscription/enable"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {"code": subscription_code, "token": token}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=data)
    resp.raise_for_status()
    return resp.json()

async def resolve_nigeria_account(account_number: str, bank_code: str):
    url = f"https://api.paystack.co/bank/resolve?account_number={account_number}&bank_code={bank_code}"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()["data"]


async def list_subscriptions_from_paystack() -> List[dict]:
    url = "https://api.paystack.co/subscription"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        logger.error(f"Failed to list subscriptions from paystack: {response.text}")
        return []