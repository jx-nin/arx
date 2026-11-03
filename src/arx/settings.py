"""Typed configuration from ``ARX_*`` environment variables and ``.env`` (spec 12).

Secrets are not read from the environment: settings hold only the path of
each secret file (spec 7.4).
"""

from collections.abc import Iterable
from pathlib import Path
from typing import Annotated, Any

from pydantic import Field, field_validator
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    NoDecode,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

KINDLE_DOMAIN = "@kindle.com"
ENV_PREFIX = "ARX_"


class _CheckedDotEnvSource(DotEnvSettingsSource):
    """Reads ``.env`` and rejects ``ARX_*`` keys that no settings class defines."""

    def __call__(self) -> dict[str, Any]:
        """Return the ``.env`` values after checking the ``ARX_*`` key names.

        :returns: Values for the settings class, by field name.
        :raises ValueError: If an ``ARX_*`` key names no field of any settings
            class, e.g. a misspelt ``ARX_SMPT_HOST``.
        """
        known = Settings.model_fields.keys() | DatabaseSettings.model_fields.keys()
        prefix = ENV_PREFIX.lower()
        unknown = sorted(
            key.upper()
            for key in self.env_vars
            if key.startswith(prefix) and key.removeprefix(prefix) not in known
        )
        if unknown:
            raise ValueError(f"unknown settings in .env: {', '.join(unknown)}")
        return super().__call__()


class _ArxSettings(BaseSettings):
    """Base of the settings classes: ``ARX_*`` variables and one shared ``.env``.

    Each class ignores the other's fields and keys of other tools (e.g. Compose's
    ``POSTGRES_*``), while misspelt ``ARX_*`` keys in ``.env`` are rejected.
    """

    model_config = SettingsConfigDict(
        env_prefix=ENV_PREFIX, env_file=".env", extra="ignore"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Replace the ``.env`` source with one that checks ``ARX_*`` key names.

        :param settings_cls: The settings class being loaded.
        :param init_settings: Values passed to the constructor.
        :param env_settings: Environment variables.
        :param dotenv_settings: The default ``.env`` source, for its file path.
        :param file_secret_settings: Secrets directory source.
        :returns: The sources in priority order.
        :raises TypeError: If pydantic-settings passes another ``.env`` source.
        """
        if not isinstance(dotenv_settings, DotEnvSettingsSource):
            raise TypeError("expected pydantic-settings' default .env source")
        checked = _CheckedDotEnvSource(
            settings_cls,
            env_file=dotenv_settings.env_file,
            env_file_encoding=dotenv_settings.env_file_encoding,
        )
        return init_settings, env_settings, checked, file_secret_settings


class Settings(_ArxSettings):
    """Arx configuration; each field reads the variable ``ARX_<FIELD>``.

    :param smtp_host: SMTP submission host.
    :param smtp_port: SMTP submission port, STARTTLS.
    :param smtp_username: SMTP login name.
    :param smtp_password_file: File holding the SMTP app password.
    :param delivery_from: Approved sender address (FR-DLV-02).
    :param delivery_allowed_recipients: Lower-cased ``@kindle.com`` addresses
        delivery may send to, comma-separated in the environment (FR-DLV-07).
    :param delivery_max_bytes: Raw attachment size limit (FR-DLV-03).
    :param arxiv_min_interval_s: Minimum seconds between arXiv requests (NFR-16).
    :param arxiv_user_agent: ``User-Agent`` for arXiv requests; ``None`` names
        Arx and the sender address as contact.
    """

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str
    smtp_password_file: Path = Path("/run/secrets/smtp_password")
    delivery_from: str
    delivery_allowed_recipients: Annotated[frozenset[str], NoDecode]
    delivery_max_bytes: int = 20 * 1024 * 1024
    arxiv_min_interval_s: float = Field(default=3.0, ge=0)
    arxiv_user_agent: str | None = None

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


class DatabaseSettings(_ArxSettings):
    """Database configuration; each field reads the variable ``ARX_<FIELD>``.

    Kept apart from :class:`Settings` so that commands without a database need
    no database settings, and migrations need no delivery settings.

    :param database_url_file: File holding the PostgreSQL URL
        (``postgresql://user:password@host/db``), which includes the password.
    """

    database_url_file: Path = Path("/run/secrets/database_url")
