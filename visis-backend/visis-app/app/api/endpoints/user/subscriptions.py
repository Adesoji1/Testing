# app/api/endpoints/user/subscriptions.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from app.services.subscription_service import (
    create_subscription,
    save_subscription,
    list_subscriptions,
    fetch_subscription,
)
from app.models.user import User
from app.schemas.subscription import SubscriptionRequest, SubscriptionResponse
from app.api.endpoints.user.auth import get_current_user
from app.database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

@router.post("/create", response_model=SubscriptionResponse)
async def subscription_create(
    subscription_request: SubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        data = create_subscription(
            email=subscription_request.email,
            plan_code=subscription_request.plan_code
        )
        # Save subscription to database
        save_subscription(data, current_user.id, db)
        return data
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[SubscriptionResponse])
async def get_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    subscriptions = list_subscriptions(db, current_user.id)
    return subscriptions

@router.get("/{subscription_code}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    subscription = fetch_subscription(db, subscription_code)
    if not subscription or subscription.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription
