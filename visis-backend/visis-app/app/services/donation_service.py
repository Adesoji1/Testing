# app/services/donation_service.py

from sqlalchemy.orm import Session
from app.models.donation import Donation
from app.schemas.donation import DonationInitializeRequest, DonationInitializeResponse
from datetime import datetime
import logging
import random
import string
from typing import Optional, Dict, Any

from app.utils.paystack_utils import initialize_transaction, verify_transaction  # Ensure these utilities are correctly implemented
from app.models.user import User  # Ensure correct import

logger = logging.getLogger(__name__)

def generate_reference(length: int = 16) -> str:
    """
    Generate a unique reference for donations.
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_authorization_url(donation: Donation) -> str:
    """
    Generate the authorization URL based on the payment channel.
    """
    return f"https://checkout.paystack.com/{donation.channel}/{donation.reference}"

async def initialize_donation(
    donation_request: DonationInitializeRequest,
    db: Session,
    current_user: User
) -> DonationInitializeResponse:
    """
    Initialize a donation by creating a record and interacting with Paystack.
    """
    reference = generate_reference()
    logger.debug(f"Generated donation reference: {reference}")

    try:
        # Initialize transaction with Paystack
        data = await initialize_transaction(
            email=donation_request.email,
            amount=donation_request.amount,
            reference=reference,
            channel=donation_request.channel,
            additional_data={
                "bank_code": donation_request.bank_code,
                "account_number": donation_request.account_number,
                "ussd_type": donation_request.ussd_type,
                "mobile_money_provider": donation_request.mobile_money_provider,
                "qr_provider": donation_request.qr_provider,
                "opay_account_number": donation_request.opay_account_number
            }
        )
        logger.debug(f"Paystack initialization data: {data}")

        # Create Donation Record
        donation = Donation(
            reference=reference,
            amount=donation_request.amount,
            currency='NGN',
            status='initialized',
            channel=donation_request.channel,
            customer_email=donation_request.email,
            first_name=donation_request.first_name,
            last_name=donation_request.last_name,
            donation_metadata=donation_request.metadata,
            user_id=current_user.id if current_user else None  # Accessing 'id' directly
        )
        db.add(donation)
        db.commit()
        db.refresh(donation)
        logger.info(f"Donation initialized with reference: {reference}")

        return DonationInitializeResponse(
            authorization_url=data.get("authorization_url", ""),
            access_code=data.get("access_code", ""),
            reference=reference
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error initializing donation: {e}")
        raise e

async def handle_donation_webhook(
    db: Session,
    reference: str
) -> bool:
    """
    Handle webhook event for a donation by verifying with Paystack and updating the record.
    """
    donation_data = await verify_transaction(reference)
    if donation_data:
        donation = db.query(Donation).filter(Donation.reference == reference).first()
        if donation:
            donation.paid_at = datetime.fromisoformat(donation_data.get('paid_at').replace('Z', '+00:00')) if donation_data.get('paid_at') else None
            donation.channel = donation_data.get('channel')
            donation.status = 'success'
            donation.authorization_code = donation_data['authorization']['authorization_code']
            donation.donation_metadata = donation_data.get('metadata')
            db.commit()
            logger.info(f"Donation {reference} marked as successful")
            return True
        else:
            logger.error(f"Donation with reference {reference} not found.")
    else:
        logger.error("Donation verification failed")
    return False

def list_donations(db: Session, user_id: int) -> list:
    """
    Retrieve all donations for a specific user.
    """
    return db.query(Donation).filter(Donation.user_id == user_id).all()

def fetch_donation(db: Session, reference: str) -> Optional[Donation]:
    """
    Retrieve a specific donation by reference.
    """
    return db.query(Donation).filter(Donation.reference == reference).first()
