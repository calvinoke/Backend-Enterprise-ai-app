
import os
import logging
import html

import httpx


logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"
RESEND_TIMEOUT_SECONDS = 20.0


def _get_email_config() -> dict:
    """Load email configuration from environment variables."""

    return {
        "api_key": os.getenv("RESEND_API_KEY", "").strip(),
        "from_email": os.getenv(
            "EMAIL_FROM",
            "Enterprise AI Platform <onboarding@resend.dev>",
        ).strip(),
        "app_env": os.getenv(
            "APP_ENV",
            "development",
        ).strip().lower(),
    }


async def _send_email(
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str,
) -> None:
    """Send an email using Resend's HTTPS API."""

    config = _get_email_config()
    api_key = config["api_key"]
    from_email = config["from_email"]
    app_env = config["app_env"]

    # Development fallback: print the message, never the API key.
    if not api_key:
        if app_env != "production":
            logger.warning(
                "RESEND_API_KEY is missing. Email was not sent. "
                "Recipient: %s; subject: %s",
                to_email,
                subject,
            )
            print(
                "\n--- DEVELOPMENT EMAIL (NOT SENT) ---\n"
                f"To: {to_email}\n"
                f"Subject: {subject}\n"
                f"{text_body}\n"
                "-------------------------------------\n"
            )
            return

        raise RuntimeError(
            "RESEND_API_KEY is not configured for production."
        )

    if not from_email:
        raise RuntimeError(
            "EMAIL_FROM is not configured."
        )

    payload = {
        "from": from_email,
        "to": [to_email],
        "subject": subject,
        "text": text_body,
        "html": html_body,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(
        timeout=RESEND_TIMEOUT_SECONDS
    ) as client:
        response = await client.post(
            RESEND_API_URL,
            json=payload,
            headers=headers,
        )

    if response.is_error:
        # Do not log API keys or other credentials.
        logger.error(
            "Resend API rejected email. HTTP status: %s; response: %s",
            response.status_code,
            response.text[:1000],
        )
        response.raise_for_status()

    result = response.json()

    logger.info(
        "Resend accepted email. Recipient: %s; email ID: %s",
        to_email,
        result.get("id", "unknown"),
    )


async def send_password_reset_email(
    to_email: str,
    reset_link: str,
    expires_minutes: int,
) -> None:
    """Send a password-reset email."""

    safe_link = html.escape(reset_link, quote=True)
    safe_expiry = int(expires_minutes)

    subject = "Reset your Enterprise AI Platform password"

    text_body = f"""
Hello,

We received a request to reset your Enterprise AI Platform password.

Open this link to reset your password:
{reset_link}

This link expires in {safe_expiry} minutes.

If you did not request a password reset, you can ignore this email.

Regards,
Enterprise AI Platform
""".strip()

    html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reset your password</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #222;">
  <h2>Reset your password</h2>
  <p>Hello,</p>
  <p>We received a request to reset your Enterprise AI Platform password.</p>
  <p>
    <a href="{safe_link}"
       style="display:inline-block;padding:12px 20px;background:#2563eb;
              color:#ffffff;text-decoration:none;border-radius:6px;">
      Reset password
    </a>
  </p>
  <p>If the button does not work, copy this link into your browser:</p>
  <p><a href="{safe_link}">{safe_link}</a></p>
  <p>This link expires in {safe_expiry} minutes.</p>
  <p>If you did not request a password reset, you can ignore this email.</p>
  <p>Regards,<br>Enterprise AI Platform</p>
</body>
</html>
""".strip()

    await _send_email(
        to_email=to_email,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )


async def send_email_verification_email(
    to_email: str,
    verification_link: str,
    expires_hours: int,
) -> None:
    """Send an email-verification message."""

    safe_link = html.escape(verification_link, quote=True)
    safe_expiry = int(expires_hours)

    subject = "Verify your Enterprise AI Platform email"

    text_body = f"""
Hello,

Thank you for creating an account on the Enterprise AI Platform.

Open this link to verify your email address:
{verification_link}

This verification link expires in {safe_expiry} hours.

If you did not create this account, you can ignore this email.

Regards,
Enterprise AI Platform
""".strip()

    html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Verify your email</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #222;">
  <h2>Verify your email address</h2>
  <p>Hello,</p>
  <p>Thank you for creating an account on the Enterprise AI Platform.</p>
  <p>Please confirm your email address by clicking below:</p>
  <p>
    <a href="{safe_link}"
       style="display:inline-block;padding:12px 20px;background:#2563eb;
              color:#ffffff;text-decoration:none;border-radius:6px;">
      Verify email address
    </a>
  </p>
  <p>If the button does not work, copy this link into your browser:</p>
  <p><a href="{safe_link}">{safe_link}</a></p>
  <p>This verification link expires in {safe_expiry} hours.</p>
  <p>If you did not create this account, you can ignore this email.</p>
  <p>Regards,<br>Enterprise AI Platform</p>
</body>
</html>
""".strip()

    await _send_email(
        to_email=to_email,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )
