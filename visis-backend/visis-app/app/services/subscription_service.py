# app/services/subscription_service.py

# import requests
# from app.core.config import settings
# from app.models.subscription import Subscription
# from sqlalchemy.orm import Session
# import logging

# logger = logging.getLogger(__name__)

# def create_subscription(email: str, plan_code: str):
#     url = "https://api.paystack.co/transaction/initialize"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#         "Content-Type": "application/json",
#     }
#     data = {
#         "email": email,
#         "plan": plan_code,
#         "callback_url": settings.PAYSTACK_CALLBACK_URL,
#     }

#     response = requests.post(url, headers=headers, json=data)
#     if response.status_code != 200:
#         logger.error(f"Paystack subscription initialization failed: {response.text}")
#         raise Exception(f"Paystack subscription initialization failed: {response.text}")
#     return response.json()["data"]

# def save_subscription(data, user_id, db: Session):
#     subscription = Subscription(
#         subscription_id=str(data['id']),
#         subscription_code=data['subscription_code'],
#         email_token=data['email_token'],
#         plan_code=data['plan'],
#         amount=data['amount'] / 100,
#         currency='NGN',  # Adjust as necessary
#         status=data['status'],
#         next_payment_date=data.get('next_payment_date'),
#         user_id=user_id
#     )
#     db.add(subscription)
#     db.commit()
#     db.refresh(subscription)
#     return subscription

# def list_subscriptions(db: Session, user_id: int):
#     return db.query(Subscription).filter(Subscription.user_id == user_id).all()

# def fetch_subscription(db: Session, subscription_code: str):
#     return db.query(Subscription).filter(Subscription.subscription_code == subscription_code).first()


# def fetch_subscription_from_paystack(subscription_code: str):
#     url = f"https://api.paystack.co/subscription/{subscription_code}"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#     }
#     response = requests.get(url, headers=headers)
#     if response.status_code == 200:
#         return response.json()["data"]
#     else:
#         logger.error(f"Failed to fetch subscription: {response.text}")
#         return None

# def list_subscriptions_from_paystack():
#     url = "https://api.paystack.co/subscription"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#     }
#     response = requests.get(url, headers=headers)
#     if response.status_code == 200:
#         return response.json()["data"]
#     else:
#         logger.error(f"Failed to list subscriptions: {response.text}")
#         return []


# app/services/subscription_service.py

import httpx
from app.core.config import settings
from app.models.subscription import Subscription
from sqlalchemy.orm import Session
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

async def create_subscription(email: str, plan_code: str) -> dict:
    """
    Initialize a subscription with Paystack.

    Args:
        email (str): User's email.
        plan_code (str): Paystack plan code.

    Returns:
        dict: Paystack response data.
    """
    url = "https://api.paystack.co/subscription"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "email": email,
        "plan": plan_code,
        "callback_url": settings.PAYSTACK_CALLBACK_URL,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
    
    if response.status_code != 200:
        logger.error(f"Paystack subscription initialization failed: {response.text}")
        raise Exception(f"Paystack subscription initialization failed: {response.text}")
    
    return response.json()["data"]

async def save_subscription(data: dict, user_id: int, db: Session) -> Subscription:
    """
    Save subscription details to the database.

    Args:
        data (dict): Paystack subscription data.
        user_id (int): ID of the user.
        db (Session): Database session.

    Returns:
        Subscription: The saved subscription object.
    """
    subscription = Subscription(
        subscription_id=str(data['id']),
        subscription_code=data['subscription_code'],
        email_token=data['email_token'],
        plan_code=data['plan']['plan_code'],  # Adjust based on Paystack's response structure
        amount=data['plan']['amount'] / 100,  # Assuming amount is in kobo
        currency=data['plan']['currency'],
        status=data['status'],
        start_date=datetime.strptime(data['start_date'], "%Y-%m-%dT%H:%M:%S.%fZ"),  # Adjust format as needed
        next_payment_date=datetime.strptime(data['next_payment_date'], "%Y-%m-%dT%H:%M:%S.%fZ") if data.get('next_payment_date') else None,
        subscription_metadata=data.get('metadata'),  # Adjust if necessary
        user_id=user_id
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    logger.info(f"Subscription {subscription.subscription_code} saved for user {user_id}")
    return subscription

def list_subscriptions(db: Session, user_id: int) -> list:
    """
    Retrieve all subscriptions for a specific user.

    Args:
        db (Session): Database session.
        user_id (int): ID of the user.

    Returns:
        list: List of Subscription objects.
    """
    return db.query(Subscription).filter(Subscription.user_id == user_id).all()

def fetch_subscription(db: Session, subscription_code: str) -> Optional[Subscription]:
    """
    Retrieve a specific subscription by subscription code.

    Args:
        db (Session): Database session.
        subscription_code (str): Subscription code.

    Returns:
        Optional[Subscription]: Subscription object if found, else None.
    """
    return db.query(Subscription).filter(Subscription.subscription_code == subscription_code).first()

async def fetch_subscription_from_paystack(subscription_code: str) -> Optional[dict]:
    """
    Fetch subscription details from Paystack.

    Args:
        subscription_code (str): Subscription code.

    Returns:
        Optional[dict]: Subscription data if successful, else None.
    """
    url = f"https://api.paystack.co/subscription/{subscription_code}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()["data"]
    else:
        logger.error(f"Failed to fetch subscription: {response.text}")
        return None

async def list_subscriptions_from_paystack() -> list:
    """
    List all subscriptions from Paystack.

    Returns:
        list: List of subscription data.
    """
    url = "https://api.paystack.co/subscription"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()["data"]
    else:
        logger.error(f"Failed to list subscriptions: {response.text}")
        return []
