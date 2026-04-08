from email.message import EmailMessage
from typing import Optional, Sequence, Tuple

import aiosmtplib

from app.core.config import settings
from app.core.logging_config import get_logger
from app.utils.exceptions import EmailSendError

logger = get_logger(__name__)


class EmailService:
    @staticmethod
    async def send_otp_email(email: str, otp_code: str) -> None:
        subject = "Verify your email"
        body = (
            "Your verification code is: "
            f"{otp_code}\n\n"
            f"This code expires in {settings.EMAIL_VERIFICATION_EXPIRE_HOURS} hour(s)."
        )
        await EmailService._send_email(email, subject, body)

    @staticmethod
    async def send_password_reset_email(email: str, otp_code: str) -> None:
        subject = "Reset your password"
        body = (
            "Your password reset code is: "
            f"{otp_code}\n\n"
            f"This code expires in {settings.PASSWORD_RESET_EXPIRE_HOURS} hour(s)."
        )
        await EmailService._send_email(email, subject, body)

    @staticmethod
    async def send_rider_purchase_invoice_email(
        email: str,
        rider_name: str,
        item_name: str,
        pdf_bytes: bytes,
        filename: str,
    ) -> None:
        subject = f"{settings.APP_NAME} rider purchase invoice"
        body = (
            f"Hello {rider_name},\n\n"
            f"Please find attached the invoice for your item purchase: {item_name}.\n"
        )
        await EmailService._send_email(
            email,
            subject,
            body,
            attachments=[(filename, pdf_bytes, "application", "pdf")],
        )

    @staticmethod
    async def _send_email(
        to_email: str,
        subject: str,
        body: str,
        attachments: Optional[Sequence[Tuple[str, bytes, str, str]]] = None,
    ) -> None:
        if not settings.SMTP_HOST:
            logger.warning(
                "SMTP_HOST is not configured; skipping email send",
                to_email=to_email,
                subject=subject,
            )
            return

        message = EmailMessage()
        message["From"] = settings.SMTP_FROM
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        for attachment in attachments or []:
            filename, content, maintype, subtype = attachment
            message.add_attachment(content, maintype=maintype, subtype=subtype, filename=filename)

        try:
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                start_tls=settings.SMTP_TLS,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
            )
            logger.info("Email sent", to_email=to_email, subject=subject)
        except Exception as exc:
            logger.error("Failed to send email", to_email=to_email, error=str(exc))
            raise EmailSendError("Failed to send email") from exc
