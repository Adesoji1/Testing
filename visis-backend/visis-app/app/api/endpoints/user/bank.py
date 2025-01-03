
# app/api/endpoints/user/bank.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas.bank import ResolveAccountNumberResponse, ValidateAccountRequest, ValidateAccountResponse, ListBanksResponse
from app.services.bank_service import resolve_account_number, validate_account, list_banks
from app.database import get_db
from app.models.user import User
from app.api.endpoints.user.auth import get_current_user
import logging
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/bank",
    tags=["bank"],
    dependencies=[Depends(get_current_user)],  # Ensure only authenticated users can access
)

@router.get("/resolve", response_model=ResolveAccountNumberResponse)
async def resolve_account(
    account_number: str, 
    bank_code: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        resolved_data = resolve_account_number(account_number, bank_code)
        return resolved_data
    except Exception as e:
        logger.error(f"Error resolving account number: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/validate", response_model=ValidateAccountResponse)
async def validate_user_account(
    validate_request: ValidateAccountRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        # Fetch customer_code associated with the current user
        customer = db.query(User).filter(User.id == current_user.id).first()
        if not customer or not customer.customer_code:
            raise HTTPException(status_code=400, detail="Customer code not found. Please register your customer first.")
        
        # Initiate account validation
        validation_data = validate_account(
            customer_code=customer.customer_code,
            country=validate_request.country,
            account_number=validate_request.account_number,
            bvn=validate_request.bvn,
            bank_code=validate_request.bank_code,
            first_name=validate_request.first_name,
            last_name=validate_request.last_name
        )
        return {"status": True, "message": "Customer Identification in progress", "data": validation_data}
    except Exception as e:
        logger.error(f"Error validating account: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/list", response_model=ListBanksResponse)
async def get_banks(
    country: Optional[str] = Query(None, description="The country from which to obtain the list of supported banks. Accepted values are: ghana, kenya, nigeria, south africa"),
    use_cursor: Optional[bool] = Query(False, description="Flag to enable cursor pagination on the endpoint"),
    per_page: Optional[int] = Query(50, ge=1, le=100, description="The number of objects to return per page. Defaults to 50, and limited to 100 records per page."),
    pay_with_bank_transfer: Optional[bool] = Query(None, description="A flag to filter for available banks a customer can make a transfer to complete a payment"),
    pay_with_bank: Optional[bool] = Query(None, description="A flag to filter for banks a customer can pay directly from"),
    enabled_for_verification: Optional[bool] = Query(None, description="A flag to filter the banks that are supported for account verification in South Africa. You need to combine this with either the currency or country filter."),
    next_cursor: Optional[str] = Query(None, description="A cursor that indicates your place in the list. It can be used to fetch the next page of the list"),
    previous_cursor: Optional[str] = Query(None, description="A cursor that indicates your place in the list. It should be used to fetch the previous page of the list after an initial next request"),
    gateway: Optional[str] = Query(None, description="The gateway type of the bank. It can be one of these: [emandate, digitalbankmandate]"),
    type_: Optional[str] = Query(None, alias="type", description="Type of financial channel. For Ghanaian channels, please use either mobile_money for mobile money channels OR ghipps for bank channels"),
    currency: Optional[str] = Query(None, description="One of the supported currency"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        banks_data = list_banks(
            country=country,
            use_cursor=use_cursor,
            per_page=per_page,
            pay_with_bank_transfer=pay_with_bank_transfer,
            pay_with_bank=pay_with_bank,
            enabled_for_verification=enabled_for_verification,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            gateway=gateway,
            type_=type_,
            currency=currency
        )
        return {
            "status": True,
            "message": "Banks retrieved",
            "data": banks_data["data"],
            "meta": banks_data.get("meta", {})
        }
    except Exception as e:
        logger.error(f"Error listing banks: {e}")
        raise HTTPException(status_code=400, detail=str(e))
