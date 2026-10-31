"""Mailer backed by the standard library's ``smtplib`` (spec 6.6.3)."""

import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

TIMEOUT_SECONDS = 60


class SmtpMailer:
    """Submits mail over SMTP with STARTTLS and password login."""

    def __init__(
        self, host: str, port: int, username: str, password_file: Path
    ) -> None:
        """Create the mailer.

        :param host: SMTP submission host, e.g. ``smtp.gmail.com``.
        :param port: Submission port that offers STARTTLS, e.g. ``587``.
        :param username: Login name.
        :param password_file: File holding the password, read on every send so
            a rotated secret applies without a restart.
        """
        self._host = host
        self._port = port
        self._username = username
        self._password_file = password_file

    def send(self, message: EmailMessage) -> None:
        """Send a message after upgrading the connection with STARTTLS.

        :param message: Complete message with sender and recipient headers.
        :raises OSError: If the password file cannot be read or the connection
            fails.
        :raises smtplib.SMTPException: If the server refuses STARTTLS, the
            login or the message.
        """
        password = self._password_file.read_text().strip()
        with smtplib.SMTP(self._host, self._port, timeout=TIMEOUT_SECONDS) as smtp:
            smtp.starttls(context=ssl.create_default_context())
            smtp.login(self._username, password)
            smtp.send_message(message)
