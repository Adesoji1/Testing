# app/api/endpoints/user/transactions.py

# app/api/endpoints/user/transactions.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from starlette.responses import Response
import logging
import random
import string

from app.schemas.transaction import (
    TransactionRequest,
    TransactionResponse,
    TransactionInitializeResponse
)
from app.services.transaction_service import (
    initialize_transaction,
    verify_transaction,
    save_transaction,
    list_transactions,
    fetch_transaction,
    update_transaction_status
)
from app.utils.paystack_utils import verify_paystack_signature
from app.utils.email_utils import send_email
from app.models.user import User
from app.models.transaction import Transaction
from app.api.endpoints.user.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/transactions", tags=["transactions"])
logger = logging.getLogger(__name__)

@router.post("/initialize", response_model=TransactionInitializeResponse)
async def transaction_initialize(
    transaction_request: TransactionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Generate a unique reference
        reference = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        
        # Initialize transaction with Paystack
        data = initialize_transaction(
            email=transaction_request.email,
            amount=transaction_request.amount,
            reference=reference
        )
        
        # Prepare transaction data for saving
        transaction_data = {
            'reference': data['reference'],
            'amount': transaction_request.amount * 100,  # Convert to Kobo
            'currency': 'NGN',
            'status': 'initialized',
            'paid_at': None,
            'channel': None,
            'customer_email': transaction_request.email,  # Ensure key matches
            'authorization_code': None,
            'user_id': current_user.id
        }
        
        # Save the transaction to the database
        save_transaction(transaction_data, db)
        
        # Return only the required fields for initialization response
        return {
            "authorization_url": data["authorization_url"],
            "access_code": data["access_code"],
            "reference": data["reference"],
        }
    except Exception as e:
        logger.error(f"Error initializing transaction: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transactions = list_transactions(db, current_user.id)
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found")
    return transactions

@router.get("/{reference}", response_model=TransactionResponse)
async def get_transaction(
    reference: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transaction = fetch_transaction(db, reference)
    if not transaction or transaction.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

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
        # Update your database, e.g., update transaction status
        update_transaction_status(reference, 'success', db)
        # Optionally, redirect to a success page
        return {"message": "Payment successful"}
    else:
        # Handle verification failure
        return {"message": "Payment verification failed"}

