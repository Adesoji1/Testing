# app/services/transaction_service.py

import requests
from app.core.config import settings
from app.models.transaction import Transaction
from sqlalchemy.orm import Session
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

def initialize_transaction(email: str, amount: float, reference: str) -> dict:
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    amount_in_kobo = int(amount * 100)
    data = {
        "email": email,
        "amount": amount_in_kobo,
        "reference": reference,
        "callback_url": settings.PAYSTACK_CALLBACK_URL,
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        logger.error(f"Paystack initialization failed: {response.text}")
        raise Exception(f"Paystack initialization failed: {response.text}")
    return response.json()["data"]

def verify_transaction(reference: str) -> Optional[dict]:
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['data']['status'] == 'success':
            return data['data']
    return None

def save_transaction(data: dict, db: Session):
    transaction = Transaction(
        reference=data['reference'],
        amount=data['amount'] / 100,  # Convert from Kobo to Naira
        currency=data.get('currency', 'NGN'),
        status=data.get('status', 'initialized'),
        paid_at=data.get('paid_at'),
        channel=data.get('channel'),
        customer_email=data['customer_email'],  # Use 'customer_email' here
        authorization_code=data.get('authorization_code'),
        user_id=data['user_id']
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

def list_transactions(db: Session, user_id: int) -> List[Transaction]:
    return db.query(Transaction).filter(Transaction.user_id == user_id).all()

def fetch_transaction(db: Session, reference: str) -> Optional[Transaction]:
    return db.query(Transaction).filter(Transaction.reference == reference).first()

def update_transaction_status(reference: str, status: str, db: Session):
    transaction = db.query(Transaction).filter(Transaction.reference == reference).first()
    if transaction:
        transaction.status = status
        db.commit()
