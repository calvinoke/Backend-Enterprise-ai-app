import asyncio
import os
import smtplib
from email.message import EmailMessage


# ============================================================
# SMTP CONFIGURATION
# ============================================================

def _get_smtp_config() -> dict:
    """
    Read SMTP configuration from environment variables.
    """

    return {
        "host": os.getenv("SMTP_HOST"),
        "port": int(
            os.getenv(
                "SMTP_PORT",
                "587",
            )
        ),
        "username": os.getenv(
            "SMTP_USERNAME"
        ),
        "password": os.getenv(
            "SMTP_PASSWORD"
        ),
        "from_email": os.getenv(
            "SMTP_FROM_EMAIL"
        ),
        "from_name": os.getenv(
            "SMTP_FROM_NAME",
            "Enterprise AI Platform",
        ),
        "app_env": os.getenv(
            "APP_ENV",
            "development",
        ).lower(),
    }


# ============================================================
# GENERIC SMTP SEND
# ============================================================

async def _send_email_message(
    message: EmailMessage,
) -> None:
    """
    Send an EmailMessage without blocking the
    asynchronous FastAPI event loop.
    """

    config = _get_smtp_config()

    smtp_host = config["host"]
    smtp_port = config["port"]
    smtp_username = config["username"]
    smtp_password = config["password"]
    app_env = config["app_env"]

    # --------------------------------------------------------
    # SMTP MUST BE CONFIGURED IN PRODUCTION
    # --------------------------------------------------------

    if not smtp_host:
        if app_env != "production":
            raise RuntimeError(
                "SMTP is not configured."
            )

        raise RuntimeError(
            "SMTP is not configured for production."
        )

    # --------------------------------------------------------
    # SEND EMAIL IN A BACKGROUND THREAD
    # --------------------------------------------------------

    def send_email() -> None:
        # ----------------------------------------------------
        # SMTP SSL
        # ----------------------------------------------------

        if smtp_port == 465:

            with smtplib.SMTP_SSL(
                smtp_host,
                smtp_port,
                timeout=15,
            ) as server:

                if (
                    smtp_username
                    and smtp_password
                ):
                    server.login(
                        smtp_username,
                        smtp_password,
                    )

                server.send_message(
                    message
                )

        # ----------------------------------------------------
        # SMTP + STARTTLS
        # ----------------------------------------------------

        else:

            with smtplib.SMTP(
                smtp_host,
                smtp_port,
                timeout=15,
            ) as server:

                server.ehlo()

                server.starttls()

                server.ehlo()

                if (
                    smtp_username
                    and smtp_password
                ):
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


# ============================================================
# PASSWORD RESET EMAIL
# ============================================================

async def send_password_reset_email(
    to_email: str,
    reset_link: str,
    expires_minutes: int,
) -> None:
    """
    Send a password-reset email.

    Development behavior:
    When SMTP is not configured, the reset link is
    printed to the terminal.

    Production behavior:
    SMTP must be configured.
    """

    config = _get_smtp_config()

    smtp_host = config["host"]
    smtp_from_email = config["from_email"]
    smtp_from_name = config["from_name"]
    app_env = config["app_env"]

    # ========================================================
    # DEVELOPMENT FALLBACK
    # ========================================================

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

    # ========================================================
    # BUILD PASSWORD RESET EMAIL
    # ========================================================

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

    # ========================================================
    # SEND
    # ========================================================

    await _send_email_message(
        message
    )


# ============================================================
# EMAIL VERIFICATION
# ============================================================

async def send_email_verification_email(
    to_email: str,
    verification_link: str,
    expires_hours: int,
) -> None:
    """
    Send an email verification message.

    Development behavior:
    When SMTP is not configured, the verification link
    is printed to the terminal.

    Production behavior:
    SMTP must be configured.
    """

    config = _get_smtp_config()

    smtp_host = config["host"]
    smtp_from_email = config["from_email"]
    smtp_from_name = config["from_name"]
    app_env = config["app_env"]

    # ========================================================
    # DEVELOPMENT FALLBACK
    # ========================================================

    if not smtp_host or not smtp_from_email:

        if app_env != "production":

            print(
                "\n"
                "=========================================\n"
                "EMAIL VERIFICATION LINK - DEVELOPMENT ONLY\n"
                "=========================================\n"
                f"Email: {to_email}\n"
                f"Verification link: {verification_link}\n"
                f"Expires in: {expires_hours} hours\n"
                "=========================================\n"
            )

            return

        raise RuntimeError(
            "SMTP is not configured for production."
        )

    # ========================================================
    # BUILD VERIFICATION EMAIL
    # ========================================================

    message = EmailMessage()

    message["Subject"] = (
        "Verify your Enterprise AI Platform email"
    )

    message["From"] = (
        f"{smtp_from_name} <{smtp_from_email}>"
    )

    message["To"] = to_email

    message.set_content(
        f"""
Hello,

Thank you for creating an account on the
Enterprise AI Platform.

Please verify your email address by opening
the following link:

{verification_link}

This verification link expires in {expires_hours} hours.

If you did not create this account, you can
safely ignore this email.

Regards,
{smtp_from_name}
""".strip()
    )

    # ========================================================
    # SEND
    # ========================================================

    await _send_email_message(
        message
    )