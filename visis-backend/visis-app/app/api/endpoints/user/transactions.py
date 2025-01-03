# app/api/endpoints/user/transactions.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import List
import logging

from app.models.transaction import Transaction
from app.schemas.transaction import (
    TransactionInitializeRequest,
    TransactionInitializeResponse,
    TransactionResponse,
    ChargeAuthorizationRequest,
    PartialDebitRequest,
)
from app.services.transaction_service import (
    initialize_transaction,
    verify_transaction,
    list_transactions,
    fetch_transaction_by_reference,
    fetch_transaction,
    charge_authorization,
    view_transaction_timeline,
    get_transaction_totals,
    export_transactions,
    partial_debit,
    handle_transaction_webhook,
)
from app.api.endpoints.user.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.utils.paystack_utils import verify_paystack_signature, verify_paystack_transaction
from fastapi.responses import Response
from app.utils.email_utils import send_email  # Ensure this utility exists

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)

@router.post("/initialize", response_model=TransactionInitializeResponse)
async def initialize_transaction_endpoint(
    transaction_request: TransactionInitializeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Initialize a transaction.
    """
    try:
        initialization_response = await initialize_transaction(
            transaction_request=transaction_request,
            db=db,
            current_user=current_user
        )
        return initialization_response
    except Exception as e:
        logger.error(f"Transaction initialization failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/verify/{reference}", response_model=TransactionResponse)
async def verify_transaction_endpoint(
    reference: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Verify a transaction using its reference.
    """
    try:
        transaction = await verify_transaction(reference=reference, db=db)
        if not transaction or transaction.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction
    except Exception as e:
        logger.error(f"Transaction verification failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/totals")
async def get_transaction_totals_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get total amount received in transactions for the current user.
    """
    try:
        totals = await get_transaction_totals(db=db, user_id=current_user.id)
        return totals
    except Exception as e:
        logger.error(f"Failed to retrieve transaction totals: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/timeline/{id_or_reference}")
async def view_transaction_timeline_endpoint(
    id_or_reference: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    timeline = await view_transaction_timeline(id_or_reference=id_or_reference)
    if not timeline:
        # If there's no timeline data, return a 404 or an appropriate message
        raise HTTPException(status_code=404, detail="No timeline data found for this transaction.")
    return timeline


@router.get("/export")
async def export_transactions_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export transactions for the current user.
    """
    try:
        export_link = await export_transactions(db=db, user_id=current_user.id)
        return {"export_link": export_link}
    except Exception as e:
        logger.error(f"Failed to export transactions: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# @router.get("/timeline/{id_or_reference}")
# async def view_transaction_timeline_endpoint(
#     id_or_reference: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """
#     View the timeline of a transaction.
#     """
#     try:
#         timeline = await view_transaction_timeline(id_or_reference=id_or_reference)
#         return timeline
#     except Exception as e:
#         logger.error(f"Failed to retrieve transaction timeline: {e}")
#         raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[TransactionResponse])
async def list_transactions_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all transactions for the current user.
    """
    transactions = list_transactions(db=db, user_id=current_user.id)
    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def fetch_transaction_endpoint(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a specific transaction by ID.
    """
    transaction = fetch_transaction(db=db, transaction_id=transaction_id)
    if not transaction or transaction.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.post("/charge_authorization", response_model=TransactionResponse)
async def charge_authorization_endpoint(
    charge_request: ChargeAuthorizationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Charge a customer’s authorization. you cannot reuse a reference that was already used in a previous successful transaction.
    Regarding the use of references:

    Does Paystack generate references?
    If you do not provide a reference field, Paystack will generate one for you automatically. This is helpful if you don't want to manage references yourself. Paystack will return the generated reference in the API response.

    What if I need a known reference?
   If you want a known, trackable reference, you must generate it yourself each time you create or charge a transaction. Each new charge attempt must have a unique reference. If you reuse a reference that was previously associated with a successful transaction, Paystack will return a "Duplicate Transaction Reference" error.

   How do clients handle references for charge_authorization?
   For ease of use, you have two options:

   Let Paystack generate the reference: Omit the reference field entirely. Paystack will respond with the generated reference in its response. You can store and use it later if needed.
   Generate your own unique reference each time you call charge_authorization. This can be a random string. It just needs to be unique so Paystack doesn’t consider it a duplicate.
   In summary:

   Remove the comment from your JSON request.
   Either omit the reference field and let Paystack create it for you or ensure you generate a unique reference each time you call charge_authorization.
    """
    try:
        transaction = await charge_authorization(
            charge_request=charge_request,
            db=db,
            current_user=current_user
        )
        return transaction
    except Exception as e:
        logger.error(f"Charge authorization failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
# @router.get("/timeline/{id_or_reference}")
# async def view_transaction_timeline_endpoint(
#     id_or_reference: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """
#     View the timeline of a transaction.
#     """
#     try:
#         timeline = await view_transaction_timeline(id_or_reference=id_or_reference)
#         return timeline
#     except Exception as e:
#         logger.error(f"Failed to retrieve transaction timeline: {e}")
#         raise HTTPException(status_code=400, detail=str(e))




# @router.get("/totals")
# async def get_transaction_totals_endpoint(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """
#     Get total amount received in transactions for the current user.
#     """
#     try:
#         totals = await get_transaction_totals(db=db, user_id=current_user.id)
#         return totals
#     except Exception as e:
#         logger.error(f"Failed to retrieve transaction totals: {e}")
#         raise HTTPException(status_code=400, detail=str(e))




@router.post("/partial_debit", response_model=TransactionResponse)
async def partial_debit_endpoint(
    partial_debit_request: PartialDebitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Perform a partial debit on a customer's account.
    """
    try:
        transaction = await partial_debit(
            partial_debit_request=partial_debit_request,
            db=db,
            current_user=current_user
        )
        return transaction
    except Exception as e:
        logger.error(f"Partial debit failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def paystack_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Handle Paystack webhook events for transactions.
    """
    is_valid = await verify_paystack_signature(request)
    if not is_valid:
        logger.warning("Unauthorized webhook attempt.")
        return Response(status_code=401)

    payload = await request.json()
    event = payload.get('event')
    data = payload.get('data')

    if event == 'charge.success':
        reference = data.get('reference')
        logger.info(f"Payment successful for reference {reference}")

        success = await handle_transaction_webhook(db=db, reference=reference)
        if success:
            # Send thank-you email in background
            transaction = fetch_transaction_by_reference(db=db, reference=reference)
            if transaction:
                email = transaction.customer_email
                amount = transaction.amount
                subject = "Thank you for your transaction"
                body = f"""
                <p>Dear {email},</p>
                <p>Thank you for your payment of NGN {amount:.2f}.</p>
                <p>Your support helps us continue our mission.</p>
                <p>Best regards,<br>Your Team</p>
                """
                background_tasks.add_task(send_email, subject, email, body)
        else:
            logger.error(f"Failed to handle webhook for reference {reference}")
    else:
        logger.info(f"Unhandled event type: {event}")

    return Response(status_code=200)

# @router.get("/callback")
# async def paystack_callback(
#     request: Request,
#     db: Session = Depends(get_db)
# ):
#     """
#     Handle Paystack callback after payment is completed.
#     """
#     reference = request.query_params.get('reference')
#     if not reference:
#         logger.error("Reference not found in callback.")
#         raise HTTPException(status_code=400, detail="Reference not found in callback.")

#     # Verify the transaction with Paystack
#     transaction_data = await verify_paystack_transaction(reference)
#     if transaction_data:
#         # Update your database, e.g., update transaction status
#         # transaction = fetch_transaction(db=db, reference=reference)
#         transaction =fetch_transaction_by_reference(db=db, reference=reference)
#         if transaction:
#             # transaction.status = 'success'
#             # transaction.paid_at = transaction_data.get('paid_at')
#             # transaction.channel = transaction_data.get('channel')
#             # transaction.authorization_code = transaction_data['authorization']['authorization_code']
#             transaction.status = transaction_data.get('status')
#             transaction.paid_at = transaction_data.get('paid_at')
#             transaction.channel = transaction_data.get('channel')
#             transaction.transaction_id = transaction_data.get('id')
#             transaction.customer_id = transaction_data['customer']['id']
#             transaction.authorization_code = transaction_data['authorization']['authorization_code']
#             transaction.currency = transaction_data.get('currency')
#             transaction.transaction_metadata = transaction_data.get('metadata')
#             db.commit()
#             return {"message": "Payment successful"}
#         else:
#             logger.error(f"Transaction with reference {reference} not found in database.")
#             raise HTTPException(status_code=404, detail="Transaction not found.")
#     else:
#         logger.error("Payment verification failed.")
#         raise HTTPException(status_code=400, detail="Payment verification failed.")
