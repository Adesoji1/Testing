# app/api/endpoints/user/donations.py

import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.schemas.donation import (
    DonationInitializeRequest,
    DonationInitializeResponse,
    DonationResponse
)
from app.services.donation_service import (
    initialize_donation,
    list_donations,
    fetch_donation,
)
from app.database import get_db
from app.models.user import User
from app.api.endpoints.user.auth import get_current_user

logger = logging.getLogger(__name__)

# Define the authenticated router with dependencies
router = APIRouter(
    prefix="/donations",
    tags=["Donations"],
    dependencies=[Depends(get_current_user)]  # Enforce authentication
)

@router.post("/initialize", response_model=DonationInitializeResponse)
async def donation_initialize(
    donation_request: DonationInitializeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Initialize a new donation.
    """
    try:
        initialization_response = await initialize_donation(
            donation_request=donation_request,
            db=db,
            current_user=current_user
        )
        return initialization_response
    except Exception as e:
        logger.error(f"Donation initialization failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[DonationResponse])
async def get_donations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all donations for the current user.
    """
    donations = list_donations(db=db, user_id=current_user.id)
    if not donations:
        raise HTTPException(status_code=404, detail="No donations found")
    return donations

@router.get("/{reference}", response_model=DonationResponse)
async def get_donation(
    reference: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a specific donation by reference.
    """
    donation = fetch_donation(db=db, reference=reference)
    if not donation or donation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Donation not found")
    return donation
