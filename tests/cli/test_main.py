import smtplib
from email.message import EmailMessage
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from arx.cli.main import main

RECIPIENT = "reader@kindle.com"


@pytest.fixture
def smtp(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> MagicMock:
    password_file = tmp_path / "smtp_password"
    password_file.write_text("app password\n")
    for name, value in {
        "ARX_SMTP_USERNAME": "arx.sender@gmail.com",
        "ARX_SMTP_PASSWORD_FILE": str(password_file),
        "ARX_DELIVERY_FROM": "arx.sender@gmail.com",
        "ARX_DELIVERY_ALLOWED_RECIPIENTS": RECIPIENT,
    }.items():
        monkeypatch.setenv(name, value)
    fake = MagicMock()
    monkeypatch.setattr(smtplib, "SMTP", fake)
    return fake


@pytest.fixture
def epub(tmp_path: Path) -> Path:
    path = tmp_path / "paper.epub"
    path.write_bytes(b"PK epub")
    return path


def send_args(epub: Path, *extra: str) -> list[str]:
    return [
        "send",
        str(epub),
        "--to",
        RECIPIENT,
        "--id",
        "2401.01234v2",
        "--title",
        "Sparse Attention for Long Documents",
        "--published",
        "2024-01-03",
        *extra,
    ]


def sent_message(smtp: MagicMock) -> EmailMessage:
    session = smtp.return_value.__enter__.return_value
    [message] = session.send_message.call_args.args
    assert isinstance(message, EmailMessage)
    return message


@pytest.mark.req("FR-DLV-02")
def test_send_mails_the_epub_described_by_the_flags(
    smtp: MagicMock, epub: Path
) -> None:
    main(send_args(epub, "--author", "Ada Lovelace", "--author", "Alan Turing"))

    message = sent_message(smtp)
    [attachment] = message.iter_attachments()
    body = message.get_body(("plain",))
    assert message["To"] == RECIPIENT
    assert message["Subject"] == "Sparse Attention for Long Documents"
    assert body is not None
    assert "arXiv:2401.01234v2" in body.get_content()
    assert attachment.get_filename() == (
        "lovelace-2024-sparse-attention-for-long-documents.epub"
    )
    assert attachment.get_content() == b"PK epub"


@pytest.mark.req("FR-DLV-02")
def test_send_without_authors_names_the_file_after_the_id(
    smtp: MagicMock, epub: Path
) -> None:
    main(send_args(epub))

    [attachment] = sent_message(smtp).iter_attachments()
    assert attachment.get_filename() == (
        "2401.01234v2-2024-sparse-attention-for-long-documents.epub"
    )


@pytest.mark.req("FR-DLV-07")
def test_send_to_a_recipient_off_the_allowlist_exits_with_the_reason(
    smtp: MagicMock, epub: Path
) -> None:
    args = send_args(epub)
    args[args.index("--to") + 1] = "other@kindle.com"

    with pytest.raises(SystemExit, match="not an allowed recipient"):
        main(args)

    smtp.assert_not_called()


def test_send_with_a_missing_epub_exits_with_the_reason(
    smtp: MagicMock, tmp_path: Path
) -> None:
    with pytest.raises(SystemExit, match="missing.epub"):
        main(send_args(tmp_path / "missing.epub"))

    smtp.assert_not_called()


def test_send_rejects_an_id_without_version(
    smtp: MagicMock, epub: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    args = send_args(epub)
    args[args.index("--id") + 1] = "2401.01234"

    with pytest.raises(SystemExit) as exit_info:
        main(args)

    assert exit_info.value.code == 2
    assert "versioned arXiv ID" in capsys.readouterr().err
