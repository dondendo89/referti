import os
import base64
import smtplib
from email.message import EmailMessage
from typing import List, Tuple
import requests


def _send_via_sendgrid(to_email: str, subject: str, body: str, attachments: List[Tuple[str, bytes, str]], from_email: str) -> None:
    api_key = os.getenv("SENDGRID_API_KEY")
    if not api_key:
        raise RuntimeError("SENDGRID_API_KEY non configurata")
    files_payload = []
    for filename, content, mime in attachments:
        files_payload.append(
            {
                "content": base64.b64encode(content).decode("utf-8"),
                "type": mime,
                "filename": filename,
                "disposition": "attachment",
            }
        )
    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": from_email},
        "subject": subject,
        "content": [{"type": "text/plain", "value": body}],
        "attachments": files_payload if files_payload else None,
    }
    resp = requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    if resp.status_code >= 300:
        raise RuntimeError(f"Errore invio SendGrid: {resp.status_code} {resp.text}")


def _send_via_smtp(to_email: str, subject: str, body: str, attachments: List[Tuple[str, bytes, str]], from_email: str) -> None:
    host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER", "")
    password = os.getenv("SMTP_PASSWORD", "")
    use_tls = os.getenv("SMTP_TLS", "true").lower() in {"1", "true", "yes"}
    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    for filename, content, mime in attachments:
        main, sub = mime.split("/", 1)
        msg.add_attachment(content, maintype=main, subtype=sub, filename=filename)
    with smtplib.SMTP(host, port, timeout=30) as server:
        if use_tls:
            server.starttls()
        if user and password:
            server.login(user, password)
        server.send_message(msg)


def send_email(to_email: str, subject: str, body: str, attachments: List[Tuple[str, bytes, str]]) -> None:
    from_email = os.getenv("FROM_EMAIL") or os.getenv("SMTP_FROM")
    if not from_email:
        raise RuntimeError("FROM_EMAIL non configurata")
    if os.getenv("SENDGRID_API_KEY"):
        _send_via_sendgrid(to_email, subject, body, attachments, from_email)
    else:
        _send_via_smtp(to_email, subject, body, attachments, from_email)