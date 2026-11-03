import smtplib
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from arx.bootstrap import build_delivery_service
from arx.domain.paper import Paper
from arx.services.delivery import AttachmentTooLargeError
from arx.settings import Settings

PAPER = Paper(
    arxiv_id="2401.01234",
    version=2,
    title="Sparse Attention for Long Documents",
    authors=("Ada Lovelace",),
    abstract="",
    published_at=datetime(2024, 1, 3, tzinfo=UTC),
    updated_at=datetime(2024, 1, 3, tzinfo=UTC),
    license=None,
)


@pytest.fixture
def smtp(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    fake = MagicMock()
    monkeypatch.setattr(smtplib, "SMTP", fake)
    return fake


def make_settings(tmp_path: Path, **overrides: object) -> Settings:
    password_file = tmp_path / "smtp_password"
    password_file.write_text("app password\n")
    fields: dict[str, object] = {
        "smtp_host": "smtp.example.com",
        "smtp_port": 2525,
        "smtp_username": "login@example.com",
        "smtp_password_file": password_file,
        "delivery_from": "arx.sender@gmail.com",
        "delivery_allowed_recipients": "reader@kindle.com",
    }
    fields.update(overrides)
    return Settings(_env_file=None, **fields)  # type: ignore[call-arg, arg-type]


@pytest.mark.req("FR-DLV-02")
def test_delivery_mails_through_the_configured_smtp_server(
    smtp: MagicMock, tmp_path: Path
) -> None:
    service = build_delivery_service(make_settings(tmp_path))

    service.send_epub(PAPER, b"PK epub", "reader@kindle.com")

    assert smtp.call_args.args == ("smtp.example.com", 2525)
    session = smtp.return_value.__enter__.return_value
    session.login.assert_called_once_with("login@example.com", "app password")
    [message] = session.send_message.call_args.args
    assert message["From"] == "arx.sender@gmail.com"


@pytest.mark.req("FR-DLV-03")
def test_delivery_uses_the_configured_size_limit(
    smtp: MagicMock, tmp_path: Path
) -> None:
    service = build_delivery_service(make_settings(tmp_path, delivery_max_bytes=3))

    with pytest.raises(AttachmentTooLargeError):
        service.send_epub(PAPER, b"PK epub", "reader@kindle.com")

    smtp.assert_not_called()
