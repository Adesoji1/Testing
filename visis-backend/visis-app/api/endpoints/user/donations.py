# app/api/endpoints/user/donations.py

from fastapi import APIRouter, HTTPException, Request, Depends
from starlette.responses import Response
from sqlalchemy.orm import Session
from app.schemas.donation import DonationRequest, DonationResponse
from app.services.donation_service import (
    initialize_donation,
    save_donation,
    update_donation_status,
    verify_transaction
)
from app.utils.paystack_utils import verify_paystack_signature
from app.utils.email_utils import send_email
from app.models.user import User
from app.api.endpoints.user.auth import get_current_user
from app.database import get_db
import logging
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from starlette.responses import Response
import logging
from typing import List
from app.services.donation_service import verify_transaction
from app.models.transaction import Transaction


router = APIRouter(prefix="/donations", tags=["donations"])

logger = logging.getLogger(__name__)

@router.post("/initialize", response_model=DonationResponse)
async def donate_initialize(
    donation_request: DonationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        data = initialize_donation(
            email=donation_request.email,
            amount=donation_request.amount,
        )
        # Save the transaction to your database
        save_donation(data, current_user.id, db)
        return data
    except Exception as e:
        logger.error(f"Error initializing donation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
@router.post("/webhook")
async def paystack_webhook(request: Request, db: Session = Depends(get_db)):
    # Verify Paystack signature
    is_valid = await verify_paystack_signature(request)
    if not is_valid:
        logger.warning("Invalid Paystack signature")
        return Response(status_code=401)
    
    # Parse the JSON payload
    payload = await request.json()
    event = payload.get('event')
    data = payload.get('data')

    if event == 'charge.success':
        reference = data.get('reference')
        logger.info(f"Payment successful for reference {reference}")

        # Verify transaction with Paystack
        transaction_data = verify_transaction(reference)
        if transaction_data:
            # Update transaction with additional details
            transaction = db.query(Transaction).filter(Transaction.reference == reference).first()
            if transaction:
                transaction.transaction_id = str(transaction_data.get('id'))
                transaction.paid_at = transaction_data.get('paid_at')
                transaction.channel = transaction_data.get('channel')
                transaction.status = 'success'
                transaction.customer_id = transaction_data['customer']['id']
                transaction.authorization_code = transaction_data['authorization']['authorization_code']
                db.commit()
            else:
                # Handle the case where transaction is not found in the database
                logger.error(f"Transaction with reference {reference} not found in database.")

            # Send email notification
            email = transaction_data['customer']['email']
            amount = transaction_data['amount'] / 100  # Convert amount from kobo to Naira
            subject = "Thank you for your donation"
            body = f"""
            <p>Dear {email},</p>
            <p>Thank you for your generous donation of NGN {amount:.2f}.</p>
            <p>Your support helps us continue our mission.</p>
            <p>Best regards,<br>Vinsighte Team</p>
            """
            send_email(subject, email, body)
        else:
            logger.error("Transaction verification failed")
    else:
        logger.info(f"Unhandled event type: {event}")
    return Response(status_code=200)

@router.get("/callback")
async def paystack_callback(request: Request, db: Session = Depends(get_db)):
    # Get the 'reference' from the query parameters
    reference = request.query_params.get('reference')
    if not reference:
        return {"message": "Reference not found in callback"}
    
    # Verify the transaction with Paystack
    transaction_data = verify_transaction(reference)
    if transaction_data:
        # Update your database, e.g., update donation status
        update_donation_status(reference, 'success', db)
        # Optionally, redirect to a success page
        return {"message": "Payment successful"}
    else:
        # Handle verification failure
        return {"message": "Payment verification failed"}


@router.get("/transactions/", response_model=List[DonationResponse])
async def get_donations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Fetching donations for user ID: {current_user.id}")
    donations = db.query(Transaction).filter(Transaction.user_id == current_user.id, Transaction.status != 'failed').all()
    if not donations:
        logger.warning(f"No donations found for user ID: {current_user.id}")
        raise HTTPException(status_code=404, detail="No donations found")
    logger.info(f"Retrieved {len(donations)} donations for user ID: {current_user.id}")
    return donations

@router.get("/{reference}", response_model=DonationResponse)
async def get_donation(
    reference: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Fetching donation with reference: {reference} for user ID: {current_user.id}")
    donation = db.query(Transaction).filter(Transaction.reference == reference, Transaction.user_id == current_user.id).first()
    if not donation:
        logger.warning(f"Donation with reference {reference} not found for user ID: {current_user.id}")
        raise HTTPException(status_code=404, detail="Donation not found")
    logger.info(f"Donation with reference {reference} retrieved successfully")
    return donation