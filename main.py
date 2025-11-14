import os
import smtplib
from email.message import EmailMessage

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

app = FastAPI(title="ZIMUT Contact API", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContactPayload(BaseModel):
    name: str
    email: EmailStr
    company: str | None = None
    message: str


def send_contact_email(payload: ContactPayload):
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")   # tu Gmail
    smtp_pass = os.getenv("SMTP_PASS")   # app password de Gmail
    contact_to = os.getenv("CONTACT_TO", smtp_user)

    # Debug rápido
    print("SMTP_USER:", repr(smtp_user))
    print("CONTACT_TO:", repr(contact_to))
    print("SMTP_HOST:", smtp_host, "PORT:", smtp_port)

    if not (smtp_user and smtp_pass and contact_to):
        raise RuntimeError("SMTP configuration is missing")

    msg = EmailMessage()
    msg["Subject"] = f"[ZIMUT] New contact: {payload.name}"
    msg["From"] = smtp_user
    msg["To"] = contact_to
    msg["Reply-To"] = payload.email

    body = f"""
New contact from the ZIMUT landing page:

Name: {payload.name}
Email: {payload.email}
Company: {payload.company or "-"}

Message:
{payload.message}
"""
    msg.set_content(body)

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/contact")
async def contact(payload: ContactPayload):
    try:
        send_contact_email(payload)
    except Exception as e:
        print("Error sending contact email:", e)
        raise HTTPException(status_code=500, detail="Error sending message")
    return {"status": "ok"}
