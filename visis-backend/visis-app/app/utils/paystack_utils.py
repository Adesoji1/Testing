# app/utils/paystack_utils.py



# app/utils/paystack_utils.py

# import hmac
# import hashlib
# import json
# from typing import Optional, Dict, Any
# import logging
# import httpx
# from app.core.config import settings
# import random
# import string

# logger = logging.getLogger(__name__)

# async def verify_paystack_signature(request) -> bool:
#     """
#     Verify the Paystack webhook signature.

#     Args:
#         request: FastAPI Request object.

#     Returns:
#         bool: True if signature is valid, False otherwise.
#     """
#     signature = request.headers.get('x-paystack-signature', '')
#     body = await request.body()
#     computed_signature = hmac.new(
#         settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
#         msg=body,
#         digestmod=hashlib.sha512
#     ).hexdigest()
#     is_valid = hmac.compare_digest(computed_signature, signature)
#     if not is_valid:
#         logger.warning("Invalid Paystack signature")
#     return is_valid


# async def create_refund(
#     transaction_reference: str,
#     amount: Optional[float] = None,
#     reference: Optional[str] = None
# ) -> Dict[str, Any]:
#     """
#     Create a refund for a transaction.

#     Args:
#         transaction_reference (str): Reference of the transaction to refund.
#         amount (Optional[float]): Amount to refund in Naira (for partial refunds).
#         reference (Optional[str]): Unique refund reference.

#     Returns:
#         Dict[str, Any]: Refund data from Paystack.
#     """
#     url = "https://api.paystack.co/refund"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#         "Content-Type": "application/json",
#     }

#     data = {
#         "transaction": transaction_reference
#     }
#     if amount:
#         data["amount"] = int(amount * 100)  # Convert to Kobo
#     if reference:
#         data["reference"] = reference
#     else:
#         data["reference"] = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.post(url, headers=headers, json=data, timeout=10.0)
#             response.raise_for_status()
#             logger.info(f"Refund created: {response.json()}")
#             return response.json()["data"]
#         except httpx.HTTPStatusError as exc:
#             logger.error(f"Refund creation failed: {exc.response.status_code} - {exc.response.text}")
#             raise Exception(f"Refund creation failed: {exc.response.text}") from exc
#         except httpx.ConnectTimeout:
#             logger.error("Connection timeout occurred while creating refund.")
#             raise Exception("Connection timeout occurred while creating refund.")
#         except Exception as exc:
#             logger.exception("An unexpected error occurred during refund creation.")
#             raise Exception(f"An unexpected error occurred: {exc}") from exc

# async def get_banks(pay_with_bank: bool = False) -> list:
#     """
#     Retrieve the list of banks, using cache to optimize.

#     Args:
#         pay_with_bank (bool): Whether to filter banks that support Pay With Bank.

#     Returns:
#         list: List of banks.
#     """
#     cache_key = f"banks_pay_with_bank_{pay_with_bank}"
#     from app.utils.redis_utils import cache_get, cache_set  # Import here to avoid circular imports

#     cached_banks = await cache_get(cache_key)
#     if cached_banks:
#         logger.info(f"Retrieved banks from cache: {cache_key}")
#         return cached_banks

#     url = "https://api.paystack.co/bank"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#     }
#     params = {"pay_with_bank": str(pay_with_bank).lower()}

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, headers=headers, params=params, timeout=10.0)
#             response.raise_for_status()
#             banks = response.json().get("data", [])
#             await cache_set(cache_key, banks, ex=3600)  # Cache for 1 hour
#             logger.info(f"Fetched and cached banks: {cache_key}")
#             return banks
#         except httpx.HTTPStatusError as exc:
#             logger.error(f"Failed to fetch banks: {exc.response.status_code} - {exc.response.text}")
#             raise Exception("Failed to fetch banks") from exc
#         except httpx.ConnectTimeout:
#             logger.error("Connection timeout occurred while fetching banks.")
#             raise Exception("Connection timeout occurred while fetching banks.")
#         except Exception as exc:
#             logger.exception("An unexpected error occurred while fetching banks.")
#             raise Exception(f"An unexpected error occurred: {exc}") from exc


# app/utils/paystack_utils.py

# import hmac
# import hashlib
# import json
# from typing import Optional, Dict, Any, List
# import logging
# import httpx
# from app.core.config import settings
# import random
# import string

# logger = logging.getLogger(__name__)

# async def verify_paystack_signature(request) -> bool:
#     """
#     Verify the Paystack webhook signature.

#     Args:
#         request: FastAPI Request object.

#     Returns:
#         bool: True if signature is valid, False otherwise.
#     """
#     signature = request.headers.get('x-paystack-signature', '')
#     body = await request.body()
#     computed_signature = hmac.new(
#         settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
#         msg=body,
#         digestmod=hashlib.sha512
#     ).hexdigest()
#     is_valid = hmac.compare_digest(computed_signature, signature)
#     if not is_valid:
#         logger.warning("Invalid Paystack signature")
#     return is_valid

# async def paystack_initialize_transaction(
#     email: str,
#     amount: float,
#     reference: str,
#     callback_url: Optional[str] = None,
#     metadata: Optional[Dict[str, Any]] = None,
#     channels: Optional[List[str]] = None,
#     currency: Optional[str] = None,
#     additional_data: Optional[Dict[str, Any]] = None
# ) -> Dict[str, Any]:
#     """
#     Initialize a transaction with Paystack.

#     Args:
#         email (str): Customer's email.
#         amount (float): Transaction amount in Naira.
#         reference (str): Unique transaction reference.
#         callback_url (Optional[str]): URL to redirect after payment.
#         metadata (Optional[Dict[str, Any]]): Additional metadata.
#         channels (Optional[List[str]]): Payment channels to make available.
#         currency (Optional[str]): Currency of the transaction.
#         additional_data (Optional[Dict[str, Any]]): Additional data based on channel.

#     Returns:
#         Dict[str, Any]: Response data from Paystack.
#     """
#     url = "https://api.paystack.co/transaction/initialize"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#         "Content-Type": "application/json",
#     }
#     amount_in_kobo = int(amount * 100)

#     data = {
#         "email": email,
#         "amount": amount_in_kobo,
#         "reference": reference,
#         "callback_url": callback_url or settings.PAYSTACK_CALLBACK_URL,
#         "metadata": metadata or {},
#         "channels": channels or ["card", "bank", "ussd", "qr", "mobile_money", "bank_transfer", "eft"],
#         "currency": currency or "NGN",
#     }

#     # Include additional data if provided
#     if additional_data:
#         data.update(additional_data)

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.post(url, headers=headers, json=data, timeout=10.0)
#             response.raise_for_status()
#             logger.info(f"Transaction initialized: {response.json()}")
#             return response.json()["data"]
#         except httpx.HTTPStatusError as exc:
#             logger.error(f"Paystack initialization failed: {exc.response.status_code} - {exc.response.text}")
#             raise Exception(f"Paystack initialization failed: {exc.response.text}") from exc
#         except httpx.ConnectTimeout:
#             logger.error("Connection timeout occurred while initializing transaction.")
#             raise Exception("Connection timeout occurred while initializing transaction.")
#         except Exception as exc:
#             logger.exception("An unexpected error occurred during transaction initialization.")
#             raise Exception(f"An unexpected error occurred: {exc}") from exc

# async def paystack_verify_transaction(reference: str) -> Optional[Dict[str, Any]]:
#     """
#     Verify a transaction's status with Paystack.

#     Args:
#         reference (str): Transaction reference.

#     Returns:
#         Optional[Dict[str, Any]]: Transaction data if successful, None otherwise.
#     """
#     url = f"https://api.paystack.co/transaction/verify/{reference}"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#     }

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, headers=headers, timeout=10.0)
#             response.raise_for_status()
#             logger.info(f"Transaction verification successful: {response.json()}")
#             return response.json().get("data")
#         except httpx.HTTPStatusError as exc:
#             logger.error(f"Transaction verification failed: {exc.response.status_code} - {exc.response.text}")
#             return None
#         except httpx.ConnectTimeout:
#             logger.error("Connection timeout occurred while verifying transaction.")
#             return None
#         except Exception as exc:
#             logger.exception("An unexpected error occurred during transaction verification.")
#             return None

# async def paystack_charge_authorization(
#     email: str,
#     amount: float,
#     authorization_code: str,
#     reference: Optional[str] = None,
#     currency: Optional[str] = None,
#     metadata: Optional[Dict[str, Any]] = None
# ) -> Dict[str, Any]:
#     """
#     Charge a customer's authorization.

#     Args:
#         email (str): Customer's email address.
#         amount (float): Amount to charge.
#         authorization_code (str): Valid authorization code to charge.
#         reference (Optional[str]): Unique transaction reference.
#         currency (Optional[str]): Currency to charge.
#         metadata (Optional[Dict[str, Any]]): Additional metadata.

#     Returns:
#         Dict[str, Any]: Response data from Paystack.
#     """
#     url = "https://api.paystack.co/transaction/charge_authorization"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#         "Content-Type": "application/json",
#     }
#     amount_in_kobo = int(amount * 100)

#     data = {
#         "email": email,
#         "amount": amount_in_kobo,
#         "authorization_code": authorization_code,
#         "reference": reference or ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
#         "currency": currency or "NGN",
#         "metadata": metadata or {},
#     }

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.post(url, headers=headers, json=data, timeout=10.0)
#             response.raise_for_status()
#             logger.info(f"Charge authorization successful: {response.json()}")
#             return response.json()["data"]
#         except httpx.HTTPStatusError as exc:
#             logger.error(f"Charge authorization failed: {exc.response.status_code} - {exc.response.text}")
#             raise Exception(f"Charge authorization failed: {exc.response.text}") from exc
#         except httpx.ConnectTimeout:
#             logger.error("Connection timeout occurred while charging authorization.")
#             raise Exception("Connection timeout occurred while charging authorization.")
#         except Exception as exc:
#             logger.exception("An unexpected error occurred during charge authorization.")
#             raise Exception(f"An unexpected error occurred: {exc}") from exc

# async def paystack_view_transaction_timeline(id_or_reference: str) -> Dict[str, Any]:
#     """
#     View the timeline of a transaction.

#     Args:
#         id_or_reference (str): Transaction ID or reference.

#     Returns:
#         Dict[str, Any]: Timeline data from Paystack.
#     """
#     url = f"https://api.paystack.co/transaction/timeline/{id_or_reference}"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#     }

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, headers=headers, timeout=10.0)
#             response.raise_for_status()
#             logger.info(f"Transaction timeline retrieved: {response.json()}")
#             return response.json().get("data")
#         except httpx.HTTPStatusError as exc:
#             logger.error(f"Failed to retrieve transaction timeline: {exc.response.status_code} - {exc.response.text}")
#             raise Exception(f"Failed to retrieve transaction timeline: {exc.response.text}") from exc
#         except httpx.ConnectTimeout:
#             logger.error("Connection timeout occurred while retrieving transaction timeline.")
#             raise Exception("Connection timeout occurred while retrieving transaction timeline.")
#         except Exception as exc:
#             logger.exception("An unexpected error occurred while retrieving transaction timeline.")
#             raise Exception(f"An unexpected error occurred: {exc}") from exc

# async def paystack_get_transaction_totals() -> Dict[str, Any]:
#     """
#     Get total amount received on your account.

#     Returns:
#         Dict[str, Any]: Transaction totals data from Paystack.
#     """
#     url = "https://api.paystack.co/transaction/totals"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#     }

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, headers=headers, timeout=10.0)
#             response.raise_for_status()
#             logger.info(f"Transaction totals retrieved: {response.json()}")
#             return response.json().get("data")
#         except httpx.HTTPStatusError as exc:
#             logger.error(f"Failed to retrieve transaction totals: {exc.response.status_code} - {exc.response.text}")
#             raise Exception(f"Failed to retrieve transaction totals: {exc.response.text}") from exc
#         except httpx.ConnectTimeout:
#             logger.error("Connection timeout occurred while retrieving transaction totals.")
#             raise Exception("Connection timeout occurred while retrieving transaction totals.")
#         except Exception as exc:
#             logger.exception("An unexpected error occurred while retrieving transaction totals.")
#             raise Exception(f"An unexpected error occurred: {exc}") from exc

# async def paystack_export_transactions() -> str:
#     """
#     Export a list of transactions.

#     Returns:
#         str: URL to the exported transactions file.
#     """
#     url = "https://api.paystack.co/transaction/export"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#     }
#     params = {
#         # Add any parameters if needed, such as date range, status, etc.
#     }

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, headers=headers, params=params, timeout=10.0)
#             response.raise_for_status()
#             logger.info(f"Transaction export initiated: {response.json()}")
#             export_data = response.json().get("data")
#             if export_data and "path" in export_data:
#                 return export_data["path"]
#             else:
#                 raise Exception("Export path not found in response.")
#         except httpx.HTTPStatusError as exc:
#             logger.error(f"Failed to export transactions: {exc.response.status_code} - {exc.response.text}")
#             raise Exception(f"Failed to export transactions: {exc.response.text}") from exc
#         except httpx.ConnectTimeout:
#             logger.error("Connection timeout occurred while exporting transactions.")
#             raise Exception("Connection timeout occurred while exporting transactions.")
#         except Exception as exc:
#             logger.exception("An unexpected error occurred while exporting transactions.")
#             raise Exception(f"An unexpected error occurred: {exc}") from exc

# async def paystack_partial_debit(
#     authorization_code: str,
#     amount: float,
#     email: str,
#     currency: Optional[str] = None,
#     reference: Optional[str] = None,
#     at_least: Optional[int] = None,
#     metadata: Optional[Dict[str, Any]] = None
# ) -> Dict[str, Any]:
#     """
#     Perform a partial debit on a customer's account.

#     Args:
#         authorization_code (str): Authorization code to charge.
#         amount (float): Amount to debit.
#         email (str): Customer's email address.
#         currency (Optional[str]): Currency to charge.
#         reference (Optional[str]): Unique transaction reference.
#         at_least (Optional[int]): Minimum amount to charge.
#         metadata (Optional[Dict[str, Any]]): Additional metadata.

#     Returns:
#         Dict[str, Any]: Response data from Paystack.
#     """
#     url = "https://api.paystack.co/transaction/partial_debit"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#         "Content-Type": "application/json",
#     }
#     amount_in_kobo = int(amount * 100)

#     data = {
#         "authorization_code": authorization_code,
#         "email": email,
#         "amount": amount_in_kobo,
#         "currency": currency or "NGN",
#         "reference": reference or ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
#         "metadata": metadata or {},
#     }
#     if at_least:
#         data["at_least"] = int(at_least * 100)

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.post(url, headers=headers, json=data, timeout=10.0)
#             response.raise_for_status()
#             logger.info(f"Partial debit successful: {response.json()}")
#             return response.json()["data"]
#         except httpx.HTTPStatusError as exc:
#             logger.error(f"Partial debit failed: {exc.response.status_code} - {exc.response.text}")
#             raise Exception(f"Partial debit failed: {exc.response.text}") from exc
#         except httpx.ConnectTimeout:
#             logger.error("Connection timeout occurred while performing partial debit.")
#             raise Exception("Connection timeout occurred while performing partial debit.")
#         except Exception as exc:
#             logger.exception("An unexpected error occurred during partial debit.")
#             raise Exception(f"An unexpected error occurred: {exc}") from exc


# app/utils/paystack_utils.py

import hmac
import hashlib
import json
from typing import Optional, Dict, Any, List
import logging
import httpx
from app.core.config import settings
import random
import string

logger = logging.getLogger(__name__)

async def verify_paystack_signature(request) -> bool:
    """
    Verify the Paystack webhook signature.

    Args:
        request: FastAPI Request object.

    Returns:
        bool: True if signature is valid, False otherwise.
    """
    signature = request.headers.get('x-paystack-signature', '')
    body = await request.body()
    computed_signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
        msg=body,
        digestmod=hashlib.sha512
    ).hexdigest()
    is_valid = hmac.compare_digest(computed_signature, signature)
    if not is_valid:
        logger.warning("Invalid Paystack signature")
    return is_valid


async def initialize_transaction(
    email: str,
    amount: float,
    reference: str,
    channel: str = "card",
    additional_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Initialize a transaction with Paystack.

    Args:
        email (str): Customer's email.
        amount (float): Transaction amount in Naira.
        reference (str): Unique transaction reference.
        channel (str): Payment channel (default: "card").
        additional_data (Optional[Dict[str, Any]]): Additional data based on channel.

    Returns:
        Dict[str, Any]: Response data from Paystack.
    """
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    amount_in_kobo = int(amount * 100)

    data = {
        "email": email,
        "amount": amount_in_kobo,
        "reference": reference,
        "callback_url": settings.PAYSTACK_CALLBACK_URL,
    }

    # Handle different channels
    if channel == "bank_transfer" and additional_data:
        data["bank_transfer"] = {
            "account_expires_at": additional_data.get("account_expires_at")
        }
    elif channel == "ussd" and additional_data:
        data["ussd"] = {
            "type": additional_data.get("ussd_type", "737")
        }
    elif channel == "mobile_money" and additional_data:
        data["mobile_money"] = {
            "phone": additional_data.get("phone"),
            "provider": additional_data.get("provider")
        }
    elif channel == "qr" and additional_data:
        data["qr"] = {
            "provider": additional_data.get("qr_provider", "visa")
        }
    elif channel == "opay" and additional_data:
        data["opay"] = {
            "account_number": additional_data.get("opay_account_number")
        }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data, timeout=10.0)
            response.raise_for_status()
            logger.info(f"Transaction initialized: {response.json()}")
            return response.json()["data"]
        except httpx.HTTPStatusError as exc:
            logger.error(f"Paystack initialization failed: {exc.response.status_code} - {exc.response.text}")
            raise Exception(f"Paystack initialization failed: {exc.response.text}") from exc
        except httpx.ConnectTimeout:
            logger.error("Connection timeout occurred while initializing transaction.")
            raise Exception("Connection timeout occurred while initializing transaction.")
        except Exception as exc:
            logger.exception("An unexpected error occurred during transaction initialization.")
            raise Exception(f"An unexpected error occurred: {exc}") from exc




async def paystack_initialize_transaction(
    email: str,
    amount: float,
    reference: str,
    callback_url: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    channels: Optional[List[str]] = None,
    currency: Optional[str] = None,
    additional_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Initialize a transaction with Paystack.

    Args:
        email (str): Customer's email.
        amount (float): Transaction amount in Naira.
        reference (str): Unique transaction reference.
        callback_url (Optional[str]): URL to redirect after payment.
        metadata (Optional[Dict[str, Any]]): Additional metadata.
        channels (Optional[List[str]]): Payment channels to make available.
        currency (Optional[str]): Currency of the transaction.
        additional_data (Optional[Dict[str, Any]]): Additional data based on channel.

    Returns:
        Dict[str, Any]: Response data from Paystack.
    """
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    amount_in_kobo = int(amount * 100)

    data = {
        "email": email,
        "amount": amount_in_kobo,
        "reference": reference,
        "callback_url": callback_url or settings.PAYSTACK_TRANSACTION_CALLBACK_URL,
        "metadata": metadata or {},
        "channels": channels or ["card", "bank", "ussd", "qr", "mobile_money", "bank_transfer", "eft"],
        "currency": currency or "NGN",
    }

    # Include additional data if provided (for transaction-specific params)
    if additional_data:
        data.update(additional_data)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data, timeout=10.0)
            response.raise_for_status()
            logger.info(f"Transaction initialized: {response.json()}")
            return response.json()["data"]
        except httpx.HTTPStatusError as exc:
            logger.error(f"Paystack initialization failed: {exc.response.status_code} - {exc.response.text}")
            raise Exception(f"Paystack initialization failed: {exc.response.text}") from exc
        except httpx.ConnectTimeout:
            logger.error("Connection timeout occurred while initializing transaction.")
            raise Exception("Connection timeout occurred while initializing transaction.")
        except Exception as exc:
            logger.exception("An unexpected error occurred during transaction initialization.")
            raise Exception(f"An unexpected error occurred: {exc}") from exc
        
async def verify_paystack_transaction(reference: str) -> Optional[Dict[str, Any]]:
    """
    Verify a transaction's status with Paystack.

    Args:
        reference (str): Transaction reference.

    Returns:
        Optional[Dict[str, Any]]: Transaction data if successful, None otherwise.
    """
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            logger.info(f"Transaction verification successful: {response.json()}")
            return response.json().get("data")
        except httpx.HTTPStatusError as exc:
            logger.error(f"Transaction verification failed: {exc.response.status_code} - {exc.response.text}")
            return None
        except httpx.ConnectTimeout:
            logger.error("Connection timeout occurred while verifying transaction.")
            return None
        except Exception as exc:
            logger.exception("An unexpected error occurred during transaction verification.")
            return None

async def paystack_verify_transaction(reference: str) -> Optional[Dict[str, Any]]:
    """
    Verify a transaction's status with Paystack.

    Args:
        reference (str): Transaction reference.

    Returns:
        Optional[Dict[str, Any]]: Transaction data if successful, None otherwise.
    """
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            logger.info(f"Transaction verification successful: {response.json()}")
            return response.json().get("data")
        except httpx.HTTPStatusError as exc:
            logger.error(f"Transaction verification failed: {exc.response.status_code} - {exc.response.text}")
            return None
        except httpx.ConnectTimeout:
            logger.error("Connection timeout occurred while verifying transaction.")
            return None
        except Exception as exc:
            logger.exception("An unexpected error occurred during transaction verification.")
            return None

async def paystack_charge_authorization(
    email: str,
    amount: float,
    authorization_code: str,
    reference: Optional[str] = None,
    currency: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Charge a customer's authorization.

    Args:
        email (str): Customer's email address.
        amount (float): Amount to charge.
        authorization_code (str): Valid authorization code to charge.
        reference (Optional[str]): Unique transaction reference.
        currency (Optional[str]): Currency to charge.
        metadata (Optional[Dict[str, Any]]): Additional metadata.

    Returns:
        Dict[str, Any]: Response data from Paystack.
    """
    url = "https://api.paystack.co/transaction/charge_authorization"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    amount_in_kobo = int(amount * 100)

    data = {
        "email": email,
        "amount": amount_in_kobo,
        "authorization_code": authorization_code,
        "reference": reference or ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
        "currency": currency or "NGN",
        "metadata": metadata or {},
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data, timeout=10.0)
            response.raise_for_status()
            logger.info(f"Charge authorization successful: {response.json()}")
            return response.json()["data"]
        except httpx.HTTPStatusError as exc:
            logger.error(f"Charge authorization failed: {exc.response.status_code} - {exc.response.text}")
            raise Exception(f"Charge authorization failed: {exc.response.text}") from exc
        except httpx.ConnectTimeout:
            logger.error("Connection timeout occurred while charging authorization.")
            raise Exception("Connection timeout occurred while charging authorization.")
        except Exception as exc:
            logger.exception("An unexpected error occurred during charge authorization.")
            raise Exception(f"An unexpected error occurred: {exc}") from exc

async def paystack_view_transaction_timeline(id_or_reference: str) -> Dict[str, Any]:
    """
    View the timeline of a transaction.

    Args:
        id_or_reference (str): Transaction ID or reference.

    Returns:
        Dict[str, Any]: Timeline data from Paystack.
    """
    url = f"https://api.paystack.co/transaction/timeline/{id_or_reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            logger.info(f"Transaction timeline retrieved: {response.json()}")
            return response.json().get("data")
        except httpx.HTTPStatusError as exc:
            logger.error(f"Failed to retrieve transaction timeline: {exc.response.status_code} - {exc.response.text}")
            raise Exception(f"Failed to retrieve transaction timeline: {exc.response.text}") from exc
        except httpx.ConnectTimeout:
            logger.error("Connection timeout occurred while retrieving transaction timeline.")
            raise Exception("Connection timeout occurred while retrieving transaction timeline.")
        except Exception as exc:
            logger.exception("An unexpected error occurred while retrieving transaction timeline.")
            raise Exception(f"An unexpected error occurred: {exc}") from exc

async def paystack_get_transaction_totals() -> Dict[str, Any]:
    """
    Get total amount received on your account.

    Returns:
        Dict[str, Any]: Transaction totals data from Paystack.
    """
    url = "https://api.paystack.co/transaction/totals"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            logger.info(f"Transaction totals retrieved: {response.json()}")
            return response.json().get("data")
        except httpx.HTTPStatusError as exc:
            logger.error(f"Failed to retrieve transaction totals: {exc.response.status_code} - {exc.response.text}")
            raise Exception(f"Failed to retrieve transaction totals: {exc.response.text}") from exc
        except httpx.ConnectTimeout:
            logger.error("Connection timeout occurred while retrieving transaction totals.")
            raise Exception("Connection timeout occurred while retrieving transaction totals.")
        except Exception as exc:
            logger.exception("An unexpected error occurred while retrieving transaction totals.")
            raise Exception(f"An unexpected error occurred: {exc}") from exc

async def paystack_export_transactions() -> str:
    """
    Export a list of transactions.

    Returns:
        str: URL to the exported transactions file.
    """
    url = "https://api.paystack.co/transaction/export"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    params = {
        # Add any parameters if needed, such as date range, status, etc.
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=10.0)
            response.raise_for_status()
            logger.info(f"Transaction export initiated: {response.json()}")
            export_data = response.json().get("data")
            if export_data and "path" in export_data:
                return export_data["path"]
            else:
                raise Exception("Export path not found in response.")
        except httpx.HTTPStatusError as exc:
            logger.error(f"Failed to export transactions: {exc.response.status_code} - {exc.response.text}")
            raise Exception(f"Failed to export transactions: {exc.response.text}") from exc
        except httpx.ConnectTimeout:
            logger.error("Connection timeout occurred while exporting transactions.")
            raise Exception("Connection timeout occurred while exporting transactions.")
        except Exception as exc:
            logger.exception("An unexpected error occurred while exporting transactions.")
            raise Exception(f"An unexpected error occurred: {exc}") from exc

async def paystack_partial_debit(
    authorization_code: str,
    amount: float,
    email: str,
    currency: Optional[str] = None,
    reference: Optional[str] = None,
    at_least: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Perform a partial debit on a customer's account.

    Args:
        authorization_code (str): Authorization code to charge.
        amount (float): Amount to debit.
        email (str): Customer's email address.
        currency (Optional[str]): Currency to charge.
        reference (Optional[str]): Unique transaction reference.
        at_least (Optional[int]): Minimum amount to charge.
        metadata (Optional[Dict[str, Any]]): Additional metadata.

    Returns:
        Dict[str, Any]: Response data from Paystack.
    """
    url = "https://api.paystack.co/transaction/partial_debit"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    amount_in_kobo = int(amount * 100)

    data = {
        "authorization_code": authorization_code,
        "email": email,
        "amount": amount_in_kobo,
        "currency": currency or "NGN",
        "reference": reference or ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
        "metadata": metadata or {},
    }
    if at_least:
        data["at_least"] = int(at_least * 100)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data, timeout=10.0)
            response.raise_for_status()
            logger.info(f"Partial debit successful: {response.json()}")
            return response.json()["data"]
        except httpx.HTTPStatusError as exc:
            logger.error(f"Partial debit failed: {exc.response.status_code} - {exc.response.text}")
            raise Exception(f"Partial debit failed: {exc.response.text}") from exc
        except httpx.ConnectTimeout:
            logger.error("Connection timeout occurred while performing partial debit.")
            raise Exception("Connection timeout occurred while performing partial debit.")
        except Exception as exc:
            logger.exception("An unexpected error occurred during partial debit.")
            raise Exception(f"An unexpected error occurred: {exc}") from exc

# Existing functions like create_refund and get_banks remain unchanged


async def create_refund(
    transaction_reference: str,
    amount: Optional[float] = None,
    reference: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a refund for a transaction.

    Args:
        transaction_reference (str): Reference of the transaction to refund.
        amount (Optional[float]): Amount to refund in Naira (for partial refunds).
        reference (Optional[str]): Unique refund reference.

    Returns:
        Dict[str, Any]: Refund data from Paystack.
    """
    url = "https://api.paystack.co/refund"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "transaction": transaction_reference
    }
    if amount:
        data["amount"] = int(amount * 100)  # Convert to Kobo
    if reference:
        data["reference"] = reference
    else:
        data["reference"] = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data, timeout=10.0)
            response.raise_for_status()
            logger.info(f"Refund created: {response.json()}")
            return response.json()["data"]
        except httpx.HTTPStatusError as exc:
            logger.error(f"Refund creation failed: {exc.response.status_code} - {exc.response.text}")
            raise Exception(f"Refund creation failed: {exc.response.text}") from exc
        except httpx.ConnectTimeout:
            logger.error("Connection timeout occurred while creating refund.")
            raise Exception("Connection timeout occurred while creating refund.")
        except Exception as exc:
            logger.exception("An unexpected error occurred during refund creation.")
            raise Exception(f"An unexpected error occurred: {exc}") from exc

async def get_banks(pay_with_bank: bool = False) -> list:
    """
    Retrieve the list of banks, using cache to optimize.

    Args:
        pay_with_bank (bool): Whether to filter banks that support Pay With Bank.

    Returns:
        list: List of banks.
    """
    cache_key = f"banks_pay_with_bank_{pay_with_bank}"
    from app.utils.redis_utils import cache_get, cache_set  # Import here to avoid circular imports

    cached_banks = await cache_get(cache_key)
    if cached_banks:
        logger.info(f"Retrieved banks from cache: {cache_key}")
        return cached_banks

    url = "https://api.paystack.co/bank"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    params = {"pay_with_bank": str(pay_with_bank).lower()}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=10.0)
            response.raise_for_status()
            banks = response.json().get("data", [])
            await cache_set(cache_key, banks, ex=3600)  # Cache for 1 hour
            logger.info(f"Fetched and cached banks: {cache_key}")
            return banks
        except httpx.HTTPStatusError as exc:
            logger.error(f"Failed to fetch banks: {exc.response.status_code} - {exc.response.text}")
            raise Exception("Failed to fetch banks") from exc
        except httpx.ConnectTimeout:
            logger.error("Connection timeout occurred while fetching banks.")
            raise Exception("Connection timeout occurred while fetching banks.")
        except Exception as exc:
            logger.exception("An unexpected error occurred while fetching banks.")
            raise Exception(f"An unexpected error occurred: {exc}") from exc


async def verify_transaction(reference: str) -> Optional[Dict[str, Any]]:
    """
    Verify a transaction's status with Paystack.

    Args:
        reference (str): Transaction reference.

    Returns:
        Optional[Dict[str, Any]]: Transaction data if successful, None otherwise.
    """
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            logger.info(f"Transaction verification successful: {response.json()}")
            return response.json().get("data")
        except httpx.HTTPStatusError as exc:
            logger.error(f"Transaction verification failed: {exc.response.status_code} - {exc.response.text}")
            return None
        except httpx.ConnectTimeout:
            logger.error("Connection timeout occurred while verifying transaction.")
            return None
        except Exception as exc:
            logger.exception("An unexpected error occurred during transaction verification.")
            return None