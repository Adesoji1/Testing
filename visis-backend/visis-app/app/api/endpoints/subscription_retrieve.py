# app/api/endpoints/subscription_retrieve.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.subscription import Subscription

router = APIRouter()

@router.get("/subscriptions/{subscription_id}")
def get_subscription(subscription_id: int, db: Session = Depends(get_db)):
    sub = db.query(Subscription).filter_by(id=subscription_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    return {
        "id": sub.id,
        "plan_code": sub.plan_code,
        "customer_code": sub.customer_code,
        "amount": sub.amount,
        "currency": sub.currency,
        "status": sub.status,
        "next_payment_date": str(sub.next_payment_date) if sub.next_payment_date else None,
        "transaction_data": sub.transaction_data
    }
