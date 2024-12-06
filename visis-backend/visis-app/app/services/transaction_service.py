# app/services/transaction_service.py
# app/services/transaction_service.py
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.schemas.transaction import (
    TransactionInitializeRequest,
    TransactionInitializeResponse,
    ChargeAuthorizationRequest,
    PartialDebitRequest,
)
from app.models.user import User
from app.utils.paystack_utils import (
    paystack_initialize_transaction,
    paystack_verify_transaction,
    paystack_charge_authorization,
    paystack_view_transaction_timeline,
    paystack_get_transaction_totals,
    paystack_export_transactions,
    paystack_partial_debit,
)
from datetime import datetime
import random
import string
import logging
from typing import List,Optional,Any ,Dict
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

async def initialize_transaction(
    transaction_request: TransactionInitializeRequest,
    db: Session,
    current_user: User
) -> TransactionInitializeResponse:
    reference = generate_reference()
    transaction_metadata = transaction_request.transaction_metadata or {}

    paystack_response = await paystack_initialize_transaction(
        email=transaction_request.email,
        amount=transaction_request.amount,
        reference=reference,
        callback_url=transaction_request.callback_url,
        metadata=transaction_metadata,
        channels=transaction_request.channels,
        currency=transaction_request.currency
    )

    transaction = Transaction(
        reference=reference,
        amount=transaction_request.amount,
        currency=transaction_request.currency or 'NGN',
        status='initialized',
        channel=','.join(transaction_request.channels) if transaction_request.channels else None,
        customer_email=transaction_request.email,
        user_id=current_user.id,
        transaction_metadata = transaction_metadata,
        created_at = datetime.now(timezone.utc)
        # created_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return TransactionInitializeResponse(
        authorization_url=paystack_response['authorization_url'],
        access_code=paystack_response['access_code'],
        reference=reference
    )

def generate_reference(length: int = 16) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# async def verify_transaction(
#     reference: str,
#     db: Session
# ) -> Transaction:
#     transaction_data = await paystack_verify_transaction(reference)
#     if transaction_data:
#         transaction = db.query(Transaction).filter(Transaction.reference == reference).first()
#         if transaction:
#             transaction.status = transaction_data.get('status')
#             transaction.paid_at = transaction_data.get('paid_at')
#             transaction.channel = transaction_data.get('channel')
#             transaction.transaction_id = transaction_data.get('id')
#             authorization = transaction_data.get('authorization')
            
#             if authorization:
#                 transaction.authorization_code = authorization.get('authorization_code')

#             transaction.customer_id = transaction_data['customer']['id']
#             transaction.currency = transaction_data.get('currency')
            
#             # Safely handle metadata
#             raw_metadata = transaction_data.get('metadata')
#             if not isinstance(raw_metadata, dict):
#                 raw_metadata = {}
#             transaction.transaction_metadata = raw_metadata
#             db.commit()
#             db.refresh(transaction)
#             return transaction
#         else:
#             logger.error(f"Transaction with reference {reference} not found in database.")
#             return None
#     else:
#         logger.error("Transaction verification failed.")
#         return None


async def verify_transaction(
    reference: str,
    db: Session
) -> Optional[Transaction]:
    transaction_data = await paystack_verify_transaction(reference)
    if transaction_data:
        transaction = db.query(Transaction).filter(Transaction.reference == reference).first()
        if not transaction:
            logger.error(f"Transaction with reference {reference} not found in database.")
            return None

        # Parse fields safely
        transaction.status = transaction_data.get('status')

        paid_at_str = transaction_data.get('paid_at')
        if paid_at_str:
            transaction.paid_at = datetime.fromisoformat(paid_at_str.replace('Z', '+00:00'))
        else:
            transaction.paid_at = None

        transaction.channel = transaction_data.get('channel')
        transaction_id_val = transaction_data.get('id')
        if transaction_id_val is not None:
            transaction.transaction_id = int(transaction_id_val)

        customer_data = transaction_data.get('customer', {})
        transaction.customer_id = customer_data.get('id')

        authorization = transaction_data.get('authorization', {})
        transaction.authorization_code = authorization.get('authorization_code')

        transaction.currency = transaction_data.get('currency')

        raw_metadata = transaction_data.get('metadata', {})
        if not isinstance(raw_metadata, dict):
            raw_metadata = {}
        transaction.transaction_metadata = raw_metadata

        db.commit()
        db.refresh(transaction)
        return transaction
    else:
        logger.error("Transaction verification failed.")
        return None

def list_transactions(db: Session, user_id: int) -> List[Transaction]:
    return db.query(Transaction).filter(Transaction.user_id == user_id).all()

def fetch_transaction_by_reference(db: Session, reference: str) -> Optional[Transaction]:
    return db.query(Transaction).filter(Transaction.reference == reference).first()


def fetch_transaction(db: Session, transaction_id: int) -> Transaction:
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()

# async def charge_authorization(
#     charge_request: ChargeAuthorizationRequest,
#     db: Session,
#     current_user: User
# ) -> Transaction:
#     paystack_response = await paystack_charge_authorization(
#         email=charge_request.email,
#         amount=charge_request.amount,
#         authorization_code=charge_request.authorization_code,
#         reference=charge_request.reference,
#         currency=charge_request.currency
#     )
#     transaction = Transaction(
#         reference=paystack_response['reference'],
#         amount=paystack_response['amount'] / 100,
#         currency=paystack_response['currency'],
#         status=paystack_response['status'],
#         channel=paystack_response['channel'],
#         customer_email=paystack_response['customer']['email'],
#         user_id=current_user.id,
#         transaction_id = paystack_response.get('id'),
#         paid_at=paystack_response['paid_at'],
#         created_at=paystack_response['transaction_date'],
#         customer_id=paystack_response['customer'].get('id') if 'customer' in paystack_response else None,
#         authorization_code=paystack_response['authorization']['authorization_code'] if 'authorization' in paystack_response else None,
#         transaction_metadata=paystack_response.get('metadata', {})
#     )
#     db.add(transaction)
#     db.commit()
#     db.refresh(transaction)
#     return transaction


async def charge_authorization(
    charge_request: ChargeAuthorizationRequest,
    db: Session,
    current_user: User
) -> Transaction:
    paystack_response = await paystack_charge_authorization(
        email=charge_request.email,
        amount=charge_request.amount,
        authorization_code=charge_request.authorization_code,
        reference=charge_request.reference or generate_reference(),
        currency=charge_request.currency,
        metadata=charge_request.metadata
    )

    # Parse fields
    paid_at_str = paystack_response.get('paid_at')
    if paid_at_str:
        paid_at_val = datetime.fromisoformat(paid_at_str.replace('Z', '+00:00'))
    else:
        paid_at_val = None

    transaction_id_val = paystack_response.get('id')
    if transaction_id_val is not None:
        transaction_id_val = int(transaction_id_val)

    customer_data = paystack_response.get('customer', {})
    authorization_data = paystack_response.get('authorization', {})

    raw_metadata = paystack_response.get('metadata', {})
    if not isinstance(raw_metadata, dict):
        raw_metadata = {}

    transaction = Transaction(
        reference=paystack_response['reference'],
        amount=paystack_response['amount'] / 100,
        currency=paystack_response['currency'],
        status=paystack_response['status'],
        channel=paystack_response['channel'],
        customer_email=customer_data.get('email', charge_request.email),
        user_id=current_user.id,
        transaction_id=transaction_id_val,
        paid_at=paid_at_val,
        created_at=paystack_response.get('transaction_date', datetime.now(timezone.utc)),
        customer_id=customer_data.get('id'),
        authorization_code=authorization_data.get('authorization_code'),
        transaction_metadata=raw_metadata
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

# async def view_transaction_timeline(
#     id_or_reference: str
# ) -> dict:
#     timeline = await paystack_view_transaction_timeline(id_or_reference)
#     return timeline

async def view_transaction_timeline(id_or_reference: str) -> Dict[str, Any]:
    """
    Fetch the transaction timeline using the provided ID or reference.

    Args:
        id_or_reference (str): The ID or reference of the transaction.

    Returns:
        Dict[str, Any]: The transaction timeline data.
    """
    try:
        timeline = await paystack_view_transaction_timeline(id_or_reference)
        logger.info(f"Successfully retrieved transaction timeline: {timeline}")
        return timeline
    except Exception as e:
        logger.error(f"Error retrieving transaction timeline for ID/reference {id_or_reference}: {e}")
        raise

async def get_transaction_totals(
    db: Session,
    user_id: int
) -> dict:
    total_amount = db.query(Transaction).filter(Transaction.user_id == user_id).with_entities(func.sum(Transaction.amount)).scalar()
    total_transactions = db.query(Transaction).filter(Transaction.user_id == user_id).count()
    return {
        "total_amount": total_amount,
        "total_transactions": total_transactions
    }

async def export_transactions(
    db: Session,
    user_id: int
) -> dict:
    """
    Export transactions for the current user.

    Args:
        db (Session): Database session.
        user_id (int): ID of the current user.

    Returns:
        dict: A dictionary containing the export link.
    """
    try:
        # Initiate the export with Paystack
        response = await paystack_export_transactions(user_id=user_id)
        
        if response.get('status'):
            export_data = response.get('data', {})
            export_link = export_data.get('path')
            expires_at = export_data.get('expiresAt')
            reference = export_data.get('reference', 'N/A')  # Adjust based on actual response

            # Add logging here
            logger.info(f"Export initiated at {datetime.now(timezone.utc).isoformat()} for user_id={user_id} with reference={reference}")

            return {"export_link": export_link}
        else:
            error_message = response.get('message', 'Unknown error during export.')
            logger.error(f"Export failed for user_id={user_id}: {error_message}")
            raise HTTPException(status_code=400, detail=error_message)
    except Exception as e:
        logger.error(f"Exception during export for user_id={user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error during export.")


# async def export_transactions(
#     db: Session,
#     user_id: int
# ) -> str:
#     export_link = await paystack_export_transactions()
#     return export_link




# async def partial_debit(
#     partial_debit_request: PartialDebitRequest,
#     db: Session,
#     current_user: User
# ) -> Transaction:
#     paystack_response = await paystack_partial_debit(
#         authorization_code=partial_debit_request.authorization_code,
#         amount=partial_debit_request.amount,
#         email=partial_debit_request.email,
#         currency=partial_debit_request.currency,
#         reference=partial_debit_request.reference,
#         at_least=partial_debit_request.at_least
#     )
#     transaction = Transaction(
#         reference=paystack_response['reference'],
#         amount=paystack_response['amount'] / 100,
#         currency=paystack_response['currency'],
#         status=paystack_response['status'],
#         channel=paystack_response['channel'],
#         customer_email=paystack_response['customer']['email'],
#         user_id=current_user.id,
#         paid_at=paystack_response['paid_at'],
#         created_at=paystack_response['transaction_date']
#     )
#     db.add(transaction)
#     db.commit()
#     db.refresh(transaction)
#     return transaction


async def export_transactions(
    db: Session,
    user_id: int
) -> str:
    export_link = await paystack_export_transactions()
    return export_link

async def partial_debit(
    partial_debit_request: PartialDebitRequest,
    db: Session,
    current_user: User
) -> Transaction:
    paystack_response = await paystack_partial_debit(
        authorization_code=partial_debit_request.authorization_code,
        amount=partial_debit_request.amount,
        email=partial_debit_request.email,
        currency=partial_debit_request.currency,
        reference=partial_debit_request.reference or generate_reference(),
        at_least=partial_debit_request.at_least
    )

    paid_at_str = paystack_response.get('paid_at')
    if paid_at_str:
        paid_at_val = datetime.fromisoformat(paid_at_str.replace('Z', '+00:00'))
    else:
        paid_at_val = None

    transaction_id_val = paystack_response.get('id')
    if transaction_id_val is not None:
        transaction_id_val = int(transaction_id_val)

    customer_data = paystack_response.get('customer', {})
    raw_metadata = paystack_response.get('metadata', {})
    if not isinstance(raw_metadata, dict):
        raw_metadata = {}

    transaction = Transaction(
        reference=paystack_response['reference'],
        amount=paystack_response['amount'] / 100,
        currency=paystack_response['currency'],
        status=paystack_response['status'],
        channel=paystack_response['channel'],
        customer_email=customer_data.get('email', partial_debit_request.email),
        user_id=current_user.id,
        paid_at=paid_at_val,
        created_at=paystack_response.get('transaction_date', datetime.now(timezone.utc)),
        customer_id=customer_data.get('id'),
        authorization_code=paystack_response.get('authorization', {}).get('authorization_code'),
        transaction_id=transaction_id_val,
        transaction_metadata=raw_metadata
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

# async def handle_transaction_webhook(
#     db: Session,
#     reference: str
# ) -> bool:
#     transaction_data = await paystack_verify_transaction(reference)
#     if transaction_data:
#         transaction = fetch_transaction_by_reference(db=db, reference=reference)
#         # transaction = db.query(Transaction).filter(Transaction.reference == reference).first()
#         if transaction:
#             transaction.status = transaction_data.get('status')
#             transaction.paid_at = transaction_data.get('paid_at')
#             transaction.channel = transaction_data.get('channel')
#             transaction.transaction_id = transaction_data.get('id')
#             authorization = transaction_data.get('authorization')
#             transaction.transaction_id = transaction_data.get('id')
#             transaction.customer_id = transaction_data['customer']['id']
#             transaction.authorization_code = transaction_data['authorization']['authorization_code']
#             transaction.currency = transaction_data.get('currency')
#             # transaction.transaction_metadata = transaction_data.get('metadata')
#             # Safely handle metadata
#             raw_metadata = transaction_data.get('metadata')
#             if not isinstance(raw_metadata, dict):
#                 raw_metadata = {}
#             transaction.transaction_metadata = raw_metadata

#             if authorization:
#                 transaction.authorization_code = authorization.get('authorization_code')
#             db.commit()
#             return True
#         else:
#             logger.error(f"Transaction with reference {reference} not found in database.")
#             return False
#     else:
#         logger.error("Transaction verification failed.")
#         return False


async def handle_transaction_webhook(
    db: Session,
    reference: str
) -> bool:
    transaction_data = await paystack_verify_transaction(reference)
    if transaction_data:
        transaction = fetch_transaction_by_reference(db=db, reference=reference)
        if not transaction:
            logger.error(f"Transaction with reference {reference} not found in database.")
            return False

        transaction.status = transaction_data.get('status')

        paid_at_str = transaction_data.get('paid_at')
        if paid_at_str:
            transaction.paid_at = datetime.fromisoformat(paid_at_str.replace('Z', '+00:00'))
        else:
            transaction.paid_at = None

        transaction.channel = transaction_data.get('channel')
        transaction_id_val = transaction_data.get('id')
        if transaction_id_val is not None:
            transaction_id_val = int(transaction_id_val)
        transaction.transaction_id = transaction_id_val

        customer_data = transaction_data.get('customer', {})
        transaction.customer_id = customer_data.get('id')

        authorization = transaction_data.get('authorization', {})
        transaction.authorization_code = authorization.get('authorization_code')

        transaction.currency = transaction_data.get('currency', 'NGN')

        raw_metadata = transaction_data.get('metadata', {})
        if not isinstance(raw_metadata, dict):
            raw_metadata = {}
        transaction.transaction_metadata = raw_metadata

        db.commit()
        return True
    else:
        logger.error("Transaction verification failed.")
        return False
