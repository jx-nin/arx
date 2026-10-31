"""Typed configuration from ``ARX_*`` environment variables and ``.env`` (spec 12).

Secrets are not read from the environment: settings hold only the path of
each secret file (spec 7.4).
"""

from collections.abc import Iterable
from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

KINDLE_DOMAIN = "@kindle.com"


class Settings(BaseSettings):
    """Arx configuration; each field reads the variable ``ARX_<FIELD>``.

    :param smtp_host: SMTP submission host.
    :param smtp_port: SMTP submission port, STARTTLS.
    :param smtp_username: SMTP login name.
    :param smtp_password_file: File holding the SMTP app password.
    :param delivery_from: Approved sender address (FR-DLV-02).
    :param delivery_allowed_recipients: Lower-cased ``@kindle.com`` addresses
        delivery may send to, comma-separated in the environment (FR-DLV-07).
    :param delivery_max_bytes: Raw attachment size limit (FR-DLV-03).
    """

    model_config = SettingsConfigDict(env_prefix="ARX_", env_file=".env")

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str
    smtp_password_file: Path = Path("/run/secrets/smtp_password")
    delivery_from: str
    delivery_allowed_recipients: Annotated[frozenset[str], NoDecode]
    delivery_max_bytes: int = 20 * 1024 * 1024

    @field_validator("delivery_allowed_recipients", mode="before")
    @classmethod
    def _check_recipients(cls, value: str | Iterable[str]) -> frozenset[str]:
        """Split a comma-separated list and check every address.

        :param value: Comma-separated string from the environment, or addresses
            passed to the constructor.
        :returns: The lower-cased addresses.
        :raises ValueError: If the list is empty or an address is not on
            ``@kindle.com``.
        """
        parts = value.split(",") if isinstance(value, str) else value
        recipients = {part.strip().lower() for part in parts} - {""}
        if not recipients:
            raise ValueError("needs at least one recipient")
        foreign = sorted(r for r in recipients if not r.endswith(KINDLE_DOMAIN))
        if foreign:
            raise ValueError(f"not {KINDLE_DOMAIN} addresses: {', '.join(foreign)}")
        return frozenset(recipients)
