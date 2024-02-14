import smtplib
import os
from email.message import EmailMessage


def email_alert(subject: str, body: str, to: str):
    msg = EmailMessage()
    msg.set_content(body)
    msg["subject"] = subject
    msg["to"] = to
    msg["from"] = "taskmaster@mail.com"
    password = os.getenv("EMAIL_PASSWORD")
    user = os.getenv("EMAIL_USER")

    server = smtplib.SMTP("localhost", 1025)
    # server.starttls()
    # server.login(user, password)
    server.send_message(msg)
    server.quit()


if __name__ == "__main__":
    email_alert("Test", "This is a test email", "target@mail.com")
