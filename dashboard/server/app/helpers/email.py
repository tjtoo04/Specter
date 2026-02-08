import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_LOGIN = os.getenv("SMTP_LOGIN")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

if not SMTP_SERVER or not SMTP_PORT or not SMTP_LOGIN or not SMTP_PASSWORD:
    raise RuntimeError("Missing SMTP Credentials")

smtp_server = SMTP_SERVER
port = SMTP_PORT
sender_email = SMTP_LOGIN
password = SMTP_PASSWORD


def send_smtp_email(receiver_email: str, otp_code: str):
    message = MIMEMultipart("alternative")
    message["Subject"] = "Login to Specter CLI"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message
    html = f"""
<html>
      <body style="font-family: sans-serif; text-align: center; padding: 20px;">
        <h2>Specter CLI Authentication</h2>
        <p>Enter the following code in your browser to complete the login:</p>
        <h1 style="background: #f4f4f4; padding: 20px; letter-spacing: 5px;">{otp_code}</h1>
        <p>This code will expire in 10 minutes.</p>
      </body>
    </html>
    """

    message.attach(MIMEText(html, "html"))

    # Connect to the server and send email
    # Use smtplib.SMTP for port 587 (STARTTLS) or smtplib.SMTP_SSL for 465
    with smtplib.SMTP(smtp_server, int(port)) as server:
        server.starttls()  # Secure the connection
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
