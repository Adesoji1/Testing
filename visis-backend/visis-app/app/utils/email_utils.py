# app/utils/email_utils.py

# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from app.core.config import settings
# import logging

# logger = logging.getLogger(__name__)

# def send_email(subject: str, recipient_email: str, body: str):
#     try:
#         msg = MIMEMultipart()
#         msg['From'] = settings.EMAIL_FROM
#         msg['To'] = recipient_email
#         msg['Subject'] = subject

#         msg.attach(MIMEText(body, 'html'))

#         server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
#         server.starttls()
#         server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
#         server.sendmail(msg['From'], msg['To'], msg.as_string())
#         server.quit()
#         logger.info(f"Email sent to {recipient_email}")
#     except Exception as e:
#         logger.error(f"Failed to send email to {recipient_email}: {e}")



# app/utils/email_utils.py

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def send_email(subject: str, recipient: str, body: str):
    try:
        message = MIMEMultipart()
        message["From"] = settings.EMAIL_FROM
        message["To"] = recipient
        message["Subject"] = subject

        message.attach(MIMEText(body, "html"))

        await aiosmtplib.send(
            message,
            hostname=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            start_tls=True
        )
        logger.info(f"Email sent to {recipient}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {e}")
