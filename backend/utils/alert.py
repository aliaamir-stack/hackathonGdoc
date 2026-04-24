# backend/utils/alert.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logger = logging.getLogger(__name__)

def send_gmail_alert(subject: str, body: str):
    """
    Sends an email alert using Gmail SMTP.
    """
    sender_email = os.getenv("GMAIL_SENDER")
    sender_password = os.getenv("GMAIL_APP_PASSWORD")
    recipient_email = os.getenv("GMAIL_RECIPIENT")

    if not all([sender_email, sender_password, recipient_email]):
        logger.warning("Gmail credentials not fully configured. Set GMAIL_SENDER, GMAIL_APP_PASSWORD, GMAIL_RECIPIENT in environment.")
        return

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        logger.info("Gmail alert sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send Gmail alert: {e}")
