# app/services/subscription_service.py

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
