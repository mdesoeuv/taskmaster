import os
import smtplib
import logging
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def email_alert(subject: str, body: str, to: str):

    user = os.getenv("EMAIL_USERNAME")
    password = os.getenv("EMAIL_PASSWORD")
    host = os.getenv("EMAIL_HOST")
    port = os.getenv("EMAIL_PORT")
    dests = os.getenv("EMAIL_DESTS")

    msg = EmailMessage()
    msg.set_content(body)
    msg["subject"] = subject
    msg["from"] = user
    msg["to"] = dests

    logging.debug(f"Sending email to {dests}")
    with smtplib.SMTP_SSL(host, port) as smtp_server:
        smtp_server.login(user, password)
        smtp_server.sendmail(user, dests, msg.as_string())
        logging.debug("Email sent successfully")


if __name__ == "__main__":

    email_alert("DEV", "Hello from app", "victor.chevillotte@gmail.com")
