# app/utils/email.py
import requests
from fastapi import BackgroundTasks
from app.core.config import settings

def send_reset_password_email(email: str, reset_link: str):
    payload = {
        "from": {"email": "no-reply@vinsighte.com.ng", "name": "Visis App"},
        "to": [{"email": email}],
        "subject": "Password Reset Request",
        "text": f"Please use the following link to reset your password: {reset_link}",
    }
    
    headers = {
        "Authorization": f"Bearer {settings.MAILTRAP_API_KEY}",  # Add Mailtrap API key in settings
        "Content-Type": "application/json"
    }

    url = "https://sandbox.api.mailtrap.io/api/send/3208713"  # Mailtrap API URL

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
