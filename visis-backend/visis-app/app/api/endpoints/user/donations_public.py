# app/api/endpoints/user/donations_public.py

import hashlib
import hmac
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.services.donation_service import (
    handle_donation_webhook,
    fetch_donation
)
from app.utils.paystack_utils import verify_transaction
from app.database import get_db
from app.core.config import settings
from app.utils.email_utils import send_email  # Ensure this utility exists

logger = logging.getLogger(__name__)

# Define the public router without authentication dependencies
public_router = APIRouter(prefix="/donations", tags=["Donations"])

@public_router.get("/callback")
async def paystack_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Paystack callback after donation is completed.
    """
    logger.debug("Entered paystack_callback endpoint")

    # Get the 'reference' from the query parameters
    reference = request.query_params.get('reference')
    if not reference:
        logger.error("Reference not found in callback.")
        raise HTTPException(status_code=400, detail="Reference not found in callback.")

    # Verify the transaction with Paystack
    donation_data = await verify_transaction(reference)
    if donation_data:
        # Update your database, e.g., update donation status
        donation = fetch_donation(db=db, reference=reference)
        if donation:
            donation.status = 'success'
            donation.paid_at = datetime.fromisoformat(
                donation_data.get('paid_at').replace('Z', '+00:00')
            ) if donation_data.get('paid_at') else None
            donation.channel = donation_data.get('channel')
            donation.authorization_code = donation_data['authorization']['authorization_code']
            db.commit()
            # Optionally, redirect to a success page or return a success message
            return {"message": "Donation successful"}
        else:
            logger.error(f"Donation with reference {reference} not found in database.")
            raise HTTPException(status_code=404, detail="Donation not found.")
    else:
        logger.error("Donation verification failed.")
        raise HTTPException(status_code=400, detail="Donation verification failed.")

@public_router.post("/webhook")
async def donation_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Handle Paystack webhook events for donations.
    """
    payload = await request.body()
    signature = request.headers.get('X-Paystack-Signature')

    if not signature:
        logger.warning("No Paystack signature found.")
        raise HTTPException(status_code=400, detail="Missing Paystack signature.")

    # Compute the expected signature using HMAC SHA512
    if not settings.PAYSTACK_SECRET_KEY:
        logger.error("PAYSTACK_SECRET_KEY is not configured.")
        raise HTTPException(status_code=500, detail="Server configuration error.")

    expected_signature = hmac.new(
        key=settings.PAYSTACK_SECRET_KEY.encode(),
        msg=payload,
        digestmod=hashlib.sha512
    ).hexdigest()

    # Compare the signatures securely to prevent timing attacks
    if not hmac.compare_digest(expected_signature, signature):
        logger.warning("Invalid webhook signature.")
        raise HTTPException(status_code=400, detail="Invalid signature.")

    # Parse the JSON payload
    payload_json = await request.json()
    event = payload_json.get('event')
    data = payload_json.get('data')

    if event == 'charge.success':
        reference = data.get('reference')
        logger.info(f"Donation successful for reference {reference}")

        success = await handle_donation_webhook(db=db, reference=reference)
        if success:
            # Fetch the donation details
            donation = fetch_donation(db=db, reference=reference)
            if donation:
                email = donation.customer_email
                amount = donation.amount
                subject = "Thank you for your donation"
                body = f"""
                <p>Dear {donation.first_name} {donation.last_name},</p>
                <p>Thank you for your generous donation of NGN {amount:.2f}.</p>
                <p>Your support helps us continue our mission.</p>
                <p>Best regards,<br>Your Team</p>
                """
                # Send thank-you email in the background
                background_tasks.add_task(send_email, subject, email, body)
            else:
                logger.error(f"Donation with reference {reference} not found in database.")
        else:
            logger.error(f"Failed to handle webhook for reference {reference}")
    else:
        logger.info(f"Unhandled event type: {event}")

    return Response(status_code=200)
