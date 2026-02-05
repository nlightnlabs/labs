
#Gmail Test
from google.oauth2 import service_account
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

import os

# Get Gmail service environment variables
SERVICE_ACCOUNT_FILE_NAME=os.getenv("GMAIL_SERVICE_ACCOUNT_FILE_NLIGHTNLABS")
DELEGATED_USER=os.getenv("GMAIL_DELEGATED_USER_NLIGHTNLABS")
DELEGATED_RECEIVER=os.getenv("GMAIL_DELEGATED_RECEIVER_NLIGHTNLABS")
SCOPES=os.getenv("GMAIL_SCOPES_NLIGHTNLABS")

# Current file path
ENVIRONMENT = os.getenv('ENVIRONMENT')
if ENVIRONMENT == "production":
    BASE_DIR = "/home/ubuntu"
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..','..', '..'))
    target_file_path = os.path.join(ROOT_DIR, SERVICE_ACCOUNT_FILE_NAME)

SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, target_file_path)
print(SERVICE_ACCOUNT_FILE)

def send_email(to_email, subject, message):
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    delegated_credentials = credentials.with_subject(DELEGATED_USER)

    service = build("gmail", "v1", credentials=delegated_credentials)

    mime_message = MIMEText(message)
    mime_message["to"] = to_email
    mime_message["subject"] = subject

    raw_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
    body = {"raw": raw_message}

    service.users().messages().send(userId="me", body=body).execute()
    print(f"✅ Email sent to {to_email}")

if __name__ == "__main__":
    send_email("avikghosh03@gmail.com", "OAuth Test Email", "Success — sent via Gmail API!")