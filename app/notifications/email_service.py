import asyncio
import os
import smtplib
from email.message import EmailMessage


async def send_password_reset_email(
    to_email: str,
    reset_link: str,
    expires_minutes: int,
) -> None:
    """
    Send a password-reset email.

    SMTP configuration is read from environment variables.

    Development behavior:
    If SMTP is not configured, the reset link is printed/logged
    so the flow can still be tested locally.

    Production behavior:
    SMTP should always be configured.
    """

    smtp_host = os.getenv(
        "SMTP_HOST"
    )

    smtp_port = int(
        os.getenv(
            "SMTP_PORT",
            "587",
        )
    )

    smtp_username = os.getenv(
        "SMTP_USERNAME"
    )

    smtp_password = os.getenv(
        "SMTP_PASSWORD"
    )

    smtp_from_email = os.getenv(
        "SMTP_FROM_EMAIL"
    )

    smtp_from_name = os.getenv(
        "SMTP_FROM_NAME",
        "Enterprise AI Platform",
    )

    frontend_url = os.getenv(
        "FRONTEND_URL",
        "http://localhost:5173",
    )

    app_env = os.getenv(
        "APP_ENV",
        "development",
    ).lower()

    # =========================================
    # DEVELOPMENT FALLBACK
    # =========================================

    if not smtp_host or not smtp_from_email:

        if app_env != "production":
            print(
                "\n"
                "=========================================\n"
                "PASSWORD RESET LINK - DEVELOPMENT ONLY\n"
                "=========================================\n"
                f"Email: {to_email}\n"
                f"Reset link: {reset_link}\n"
                f"Expires in: {expires_minutes} minutes\n"
                "=========================================\n"
            )

            return

        raise RuntimeError(
            "SMTP is not configured for production."
        )

    # =========================================
    # BUILD EMAIL
    # =========================================

    message = EmailMessage()

    message["Subject"] = (
        "Reset your Enterprise AI Platform password"
    )

    message["From"] = (
        f"{smtp_from_name} <{smtp_from_email}>"
    )

    message["To"] = to_email

    message.set_content(
        f"""
Hello,

We received a request to reset your password
for the Enterprise AI Platform.

Use the following link to create a new password:

{reset_link}

This link expires in {expires_minutes} minutes.

If you did not request a password reset, you can
safely ignore this email.

Regards,
{smtp_from_name}
""".strip()
    )

    # =========================================
    # SEND EMAIL WITHOUT BLOCKING ASYNC SERVER
    # =========================================

    def send_email() -> None:

        if smtp_port == 465:

            with smtplib.SMTP_SSL(
                smtp_host,
                smtp_port,
                timeout=15,
            ) as server:

                if smtp_username and smtp_password:
                    server.login(
                        smtp_username,
                        smtp_password,
                    )

                server.send_message(
                    message
                )

        else:

            with smtplib.SMTP(
                smtp_host,
                smtp_port,
                timeout=15,
            ) as server:

                server.ehlo()
                server.starttls()
                server.ehlo()

                if smtp_username and smtp_password:
                    server.login(
                        smtp_username,
                        smtp_password,
                    )

                server.send_message(
                    message
                )

    await asyncio.to_thread(
        send_email
    )