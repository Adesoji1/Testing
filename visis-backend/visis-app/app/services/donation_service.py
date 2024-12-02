# # app/services/donation_service.py

# import requests
# import random
# import string
# import logging
# from app.core.config import settings
# from app.models.donation import Donation
# from app.models.transaction import Transaction

# logger = logging.getLogger(__name__)

# def initialize_donation(email: str, amount: float):
#     url = "https://api.paystack.co/transaction/initialize"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#         "Content-Type": "application/json",
#     }
#     amount_in_kobo = int(amount * 100)
#     reference = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))

#     data = {
#         "email": email,
#         "amount": amount_in_kobo,
#         "reference": reference,
#         "callback_url": settings.PAYSTACK_CALLBACK_URL,
#         "plan": settings.PAYSTACK_PLAN_CODE,
#     }

#     response = requests.post(url, headers=headers, json=data)
#     if response.status_code != 200:
#         logger.error(f"Paystack initialization failed: {response.text}")
#         raise Exception(f"Paystack initialization failed: {response.text}")
#     return response.json()["data"]

# # app/services/donation_service.py

# # ... existing imports ...

# def save_donation(data, user, db):
#     new_donation = Donation(
#         reference=data['reference'],
#         amount=data['amount'] / 100,  # Convert back to Naira
#         email=data['email'],
#         status='initialized',
#         user_id=user.id
#     )
#     db.add(new_donation)
#     db.commit()
#     db.refresh(new_donation)
#     return new_donation

# def update_donation_status(reference, status, db):
#     donation = db.query(Donation).filter(Donation.reference == reference).first()
#     if donation:
#         donation.status = status
#         db.commit()


# def verify_transaction(reference: str):
#     url = f"https://api.paystack.co/transaction/verify/{reference}"
#     headers = {
#         "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#         "Content-Type": "application/json",
#     }
#     response = requests.get(url, headers=headers)
#     if response.status_code == 200:
#         data = response.json()
#         if data['data']['status'] == 'success':
#             return True
#     return False



# app/services/donation_service.py

import requests
import random
import string
import logging
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.transaction import Transaction

logger = logging.getLogger(__name__)

def initialize_donation(email: str, amount: float):
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    amount_in_kobo = int(amount * 100)
    reference = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))

    data = {
        "email": email,
        "amount": amount_in_kobo,
        "reference": reference,
        "callback_url": settings.PAYSTACK_CALLBACK_URL,
        # Include "plan" if necessary
        "plan": settings.PAYSTACK_PLAN_CODE,
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        logger.error(f"Paystack initialization failed: {response.text}")
        raise Exception(f"Paystack initialization failed: {response.text}")
    # return response.json()["data"]

    paystack_data = response.json()["data"]
    # Add 'amount' and 'email' to the data dictionary
    paystack_data['amount'] = amount * 100  # Store amount in kobo
    paystack_data['email'] = email

    return paystack_data

def save_donation(data, user_id, db: Session):
    transaction = Transaction(
        transaction_id=None,
        reference=data['reference'],
        amount=data['amount'] / 100,  # Convert to Naira
        currency='NGN',
        status='initialized',
        paid_at=None,
        channel=None,
        customer_email=data['email'],
        customer_id=None,
        authorization_code=None,
        user_id=user_id
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

def update_donation_status(reference, status, db: Session):
    transaction = db.query(Transaction).filter(Transaction.reference == reference).first()
    if transaction:
        transaction.status = status
        db.commit()

def verify_transaction(reference: str):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['data']['status'] == 'success':
            return data['data']
    return None
