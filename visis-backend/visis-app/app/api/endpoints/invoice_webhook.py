from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.paystack_utils import verify_paystack_signature
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/invoice/webhook")
async def invoice_webhook(request: Request, db: Session = Depends(get_db)):
    # Handle invoice events (invoice.create, invoice.update, invoice.payment_failed)
    # Save invoice info or log it
    if not await verify_paystack_signature(request):
        raise HTTPException(status_code=400, detail="Invalid signature")

    body = await request.json()
    event = body.get("event")
    data = body.get("data")

    logger.info(f"Received invoice event {event}: {data}")

    # You can store data in an Invoice model, or handle accordingly
    invoice_code = data["invoice_code"], status = data["status"]
    amount = data["amount"]

    return {"status": "ok"}
