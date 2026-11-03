"""Composition root: builds services with their concrete adapters (spec 5.2)."""

from arx.adapters.mail.smtp_mailer import SmtpMailer
from arx.services.delivery import DeliveryService
from arx.settings import Settings


def build_delivery_service(settings: Settings) -> DeliveryService:
    """Build the delivery service with the SMTP mailer (spec 6.6.3).

    :param settings: Loaded configuration.
    :returns: A service that mails EPUBs through the configured SMTP server.
    """
    mailer = SmtpMailer(
        settings.smtp_host,
        settings.smtp_port,
        settings.smtp_username,
        settings.smtp_password_file,
    )
    return DeliveryService(
        mailer,
        settings.delivery_from,
        settings.delivery_allowed_recipients,
        settings.delivery_max_bytes,
    )
