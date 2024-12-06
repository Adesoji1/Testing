# app/api/endpoints/transactions_public.py

from fastapi import APIRouter, HTTPException, Request, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi.responses import Response
import logging

from app.database import get_db
from app.utils.paystack_utils import verify_paystack_transaction, verify_paystack_signature
from app.services.transaction_service import fetch_transaction_by_reference
from app.utils.email_utils import send_email

logger = logging.getLogger(__name__)

public_router = APIRouter(prefix="/transactions", tags=["Transactions-Public"])

@public_router.get("/callback")
async def paystack_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Paystack callback after payment is completed.
    Public route: No get_current_user dependency.
    """
    reference = request.query_params.get('reference')
    if not reference:
        logger.error("Reference not found in callback.")
        raise HTTPException(status_code=400, detail="Reference not found in callback.")

    # Verify the transaction with Paystack
    transaction_data = await verify_paystack_transaction(reference)
    if transaction_data:
        transaction = fetch_transaction_by_reference(db=db, reference=reference)
        if transaction:
            # Update transaction fields
            transaction.status = transaction_data.get('status')
            transaction.paid_at = transaction_data.get('paid_at')
            transaction.channel = transaction_data.get('channel')
            transaction.transaction_id = transaction_data.get('id')
            transaction.customer_id = transaction_data['customer']['id']
            transaction.authorization_code = transaction_data['authorization']['authorization_code']
            transaction.currency = transaction_data.get('currency')
            transaction.transaction_metadata = transaction_data.get('metadata')
            db.commit()
            return {"message": "Payment successful"}
        else:
            logger.error(f"Transaction with reference {reference} not found in database.")
            raise HTTPException(status_code=404, detail="Transaction not found.")
    else:
        logger.error("Payment verification failed.")
        raise HTTPException(status_code=400, detail="Payment verification failed.")
