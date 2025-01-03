import requests
from app.core.config import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def resolve_account_number(account_number: str, bank_code: str):
    url = "https://api.paystack.co/bank/resolve"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    params = {
        "account_number": account_number,
        "bank_code": bank_code
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        logger.error(f"Failed to resolve account number: {response.text}")
        raise Exception("Failed to resolve account number.")
    
    data = response.json()
    if not data.get("status"):
        logger.error(f"Resolve account number failed: {data.get('message')}")
        raise Exception(data.get("message", "Resolve account number failed."))
    
    return data["data"]
def validate_account(customer_code: str, country: str, account_number: str, bvn: str, bank_code: str, first_name: str, last_name: str):
    """
    Initiates bank account validation for a customer.
    """
    url = f"https://api.paystack.co/customer/{customer_code}/identification"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "country": country,
        "type": "bank_account",
        "account_number": account_number,
        "bvn": bvn,
        "bank_code": bank_code,
        "first_name": first_name,
        "last_name": last_name
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        logger.error(f"Failed to validate account: {response.text}")
        raise Exception("Failed to validate account.")
    
    data = response.json()
    if not data.get("status"):
        logger.error(f"Validate account failed: {data.get('message')}")
        raise Exception(data.get("message", "Validate account failed."))
    
    return data["data"]


# app/services/bank_service.py

def list_banks(
    country: Optional[str] = None,
    use_cursor: Optional[bool] = False,
    per_page: Optional[int] = 50,
    pay_with_bank_transfer: Optional[bool] = None,
    pay_with_bank: Optional[bool] = None,
    enabled_for_verification: Optional[bool] = None,
    next_cursor: Optional[str] = None,
    previous_cursor: Optional[str] = None,
    gateway: Optional[str] = None,
    type_: Optional[str] = None,  # 'type' is a reserved keyword
    currency: Optional[str] = None
):
    url = "https://api.paystack.co/bank"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    params = {}
    if country:
        params["country"] = country
    if use_cursor is not None:
        params["use_cursor"] = str(use_cursor).lower()
    if per_page:
        params["perPage"] = per_page
    if pay_with_bank_transfer is not None:
        params["pay_with_bank_transfer"] = str(pay_with_bank_transfer).lower()
    if pay_with_bank is not None:
        params["pay_with_bank"] = str(pay_with_bank).lower()
    if enabled_for_verification is not None:
        params["enabled_for_verification"] = str(enabled_for_verification).lower()
    if next_cursor:
        params["next"] = next_cursor
    if previous_cursor:
        params["previous"] = previous_cursor
    if gateway:
        params["gateway"] = gateway
    if type_:
        params["type"] = type_
    if currency:
        params["currency"] = currency

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        logger.error(f"Failed to list banks: {response.text}")
        raise Exception("Failed to list banks.")
    
    data = response.json()
    if not data.get("status"):
        logger.error(f"List banks failed: {data.get('message')}")
        raise Exception(data.get("message", "List banks failed."))
    
    return data["data"]


# def create_paystack_plan(plan_code: str, name: str, amount: int, interval: str, currency: str = "NGN", description: str = ""):
#     """
#     Creates a subscription plan on Paystack.
#     """
#     url = "https://api.paystack.co/plan"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#         "Content-Type": "application/json",
#     }
#     payload = {
#         "name": name,
#         "amount": amount,
#         "interval": interval,
#         "currency": currency,
#         "plan_code": plan_code,
#         "description": description
#     }
#     response = requests.post(url, headers=headers, json=payload)
#     if response.status_code != 200:
#         logger.error(f"Failed to create Paystack plan: {response.text}")
#         raise Exception("Failed to create Paystack plan.")
    
#     data = response.json()
#     if not data.get("status"):
#         logger.error(f"Paystack plan creation failed: {data.get('message')}")
#         raise Exception(data.get("message", "Paystack plan creation failed."))
    
#     return data["data"]

# app/services/bank_service.py

# def create_paystack_plan(plan_code: str, name: str, amount: int, interval: str, currency: str = "NGN", description: str = ""):
#     """
#     Creates a subscription plan on Paystack.
#     If the plan already exists, fetches its details.
#     """
#     url = "https://api.paystack.co/plan"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#         "Content-Type": "application/json",
#     }
#     payload = {
#         "name": name,
#         "amount": amount,
#         "interval": interval,
#         "currency": currency,
#         "plan_code": plan_code,
#         "description": description
#     }
#     response = requests.post(url, headers=headers, json=payload)
#     if response.status_code == 400 and "Plan code already exists" in response.text:
#         logger.warning(f"Plan code {plan_code} already exists on Paystack.")
#         # Optionally, fetch the existing plan details
#         return get_paystack_plan(plan_code)
#     elif response.status_code != 200:
#         logger.error(f"Failed to create Paystack plan: {response.text}")
#         raise Exception("Failed to create Paystack plan.")
    
#     data = response.json()
#     if not data.get("status"):
#         logger.error(f"Paystack plan creation failed: {data.get('message')}")
#         raise Exception(data.get("message", "Paystack plan creation failed."))
    
#     return data["data"]



def create_paystack_plan(name: str, amount: int, interval: str, code: str):
    url = "https://api.paystack.co/plan"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "name": name,
        "amount": amount,
        "interval": interval,
        "code": code  # Correct parameter
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code != 200:
        logger.error(f"Failed to create Paystack plan: {response.text}")
        raise Exception("Failed to create Paystack plan.")
    
    response_data = response.json()
    if not response_data.get("status"):
        logger.error(f"Paystack plan creation error: {response_data.get('message')}")
        raise Exception(response_data.get("message", "Plan creation failed on Paystack."))
    
    logger.info(f"Plan created on Paystack: {response_data['data']['code']}")
    return response_data["data"]

def get_paystack_plan(plan_code: str):
    """
    Retrieves a plan from Paystack by its plan_code.
    """
    url = f"https://api.paystack.co/plan/{plan_code}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logger.error(f"Failed to retrieve Paystack plan: {response.text}")
        raise Exception("Failed to retrieve Paystack plan.")
    
    data = response.json()
    if not data.get("status"):
        logger.error(f"Paystack plan retrieval failed: {data.get('message')}")
        raise Exception(data.get("message", "Paystack plan retrieval failed."))
    
    return data["data"]
