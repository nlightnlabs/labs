import boto3
import os
from email.message import EmailMessage
from typing import List, Optional
from pydantic import BaseModel


SES_REGION = "us-west-2"
FROM_EMAIL = "solutions@illuminis.ai"

ENVIRONMENT = os.getenv("ENVIRONMENT", "").lower()

if ENVIRONMENT == "development":
    ses = boto3.Session(profile_name="illuminis").client(
        "ses", region_name=SES_REGION
    )
else:
    ses = boto3.client("ses", region_name=SES_REGION)


class EmailAttachment(BaseModel):
    filename: str
    content: bytes          # base64-decoded bytes
    content_type: str       # e.g. "application/pdf"

class EmailPayload(BaseModel):
    to_email: List[str]
    subject: str
    body: str
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    attachments: Optional[List[EmailAttachment]] = None

async def send_email(request: EmailPayload):

    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = ", ".join(request.to_email)
    msg["Subject"] = request.subject

    if request.cc:
        msg["Cc"] = ", ".join(request.cc)

    if request.bcc:
        msg["Bcc"] = ", ".join(request.bcc)

    msg.set_content(request.body)

    # Attachments
    if request.attachments:
        for att in request.attachments:
            msg.add_attachment(
                att.content,
                maintype=att.content_type.split("/")[0],
                subtype=att.content_type.split("/")[1],
                filename=att.filename,
            )

    # SES requires explicit destinations
    destinations = (
        request.to_email
        + (request.cc or [])
        + (request.bcc or [])
    )

    ses.send_raw_email(
        Source=FROM_EMAIL,
        Destinations=destinations,
        RawMessage={"Data": msg.as_bytes()},
    )
