import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path
from types import TracebackType

import pytest

from arx.adapters.mail import smtp_mailer
from arx.adapters.mail.smtp_mailer import SmtpMailer


class FakeSmtp:
    instances: list[FakeSmtp] = []

    def __init__(self, host: str, port: int, timeout: float) -> None:
        self.address = (host, port, timeout)
        self.calls: list[tuple[str, object]] = []
        FakeSmtp.instances.append(self)

    def __enter__(self) -> FakeSmtp:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.calls.append(("quit", None))

    def starttls(self, context: ssl.SSLContext) -> None:
        self.calls.append(("starttls", context))

    def login(self, user: str, password: str) -> None:
        self.calls.append(("login", (user, password)))

    def send_message(self, message: EmailMessage) -> None:
        self.calls.append(("send_message", message))


@pytest.fixture
def fake_smtp(monkeypatch: pytest.MonkeyPatch) -> type[FakeSmtp]:
    FakeSmtp.instances = []
    monkeypatch.setattr(smtplib, "SMTP", FakeSmtp)
    return FakeSmtp


@pytest.fixture
def password_file(tmp_path: Path) -> Path:
    path = tmp_path / "smtp_password"
    path.write_text("abcd efgh ijkl mnop\n")
    return path


@pytest.mark.req("FR-DLV-02")
def test_sends_over_starttls_after_logging_in(
    fake_smtp: type[FakeSmtp], password_file: Path
) -> None:
    message = EmailMessage()
    mailer = SmtpMailer("smtp.gmail.com", 587, "arx.sender@gmail.com", password_file)

    mailer.send(message)

    [smtp] = fake_smtp.instances
    assert smtp.address == ("smtp.gmail.com", 587, smtp_mailer.TIMEOUT_SECONDS)
    assert [name for name, _ in smtp.calls] == [
        "starttls",
        "login",
        "send_message",
        "quit",
    ]
    assert smtp.calls[1][1] == ("arx.sender@gmail.com", "abcd efgh ijkl mnop")
    assert smtp.calls[2][1] is message


@pytest.mark.req("FR-DLV-02")
def test_starttls_verifies_the_server_certificate(
    fake_smtp: type[FakeSmtp], password_file: Path
) -> None:
    SmtpMailer("smtp.gmail.com", 587, "u", password_file).send(EmailMessage())

    context = fake_smtp.instances[0].calls[0][1]
    assert isinstance(context, ssl.SSLContext)
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname


@pytest.mark.req("FR-DLV-02")
def test_reads_the_password_file_on_every_send(
    fake_smtp: type[FakeSmtp], password_file: Path
) -> None:
    mailer = SmtpMailer("smtp.gmail.com", 587, "u", password_file)
    mailer.send(EmailMessage())
    password_file.write_text("rotated")

    mailer.send(EmailMessage())

    assert fake_smtp.instances[1].calls[1][1] == ("u", "rotated")


@pytest.mark.req("FR-DLV-02")
def test_missing_password_file_fails_before_connecting(
    fake_smtp: type[FakeSmtp], tmp_path: Path
) -> None:
    mailer = SmtpMailer("smtp.gmail.com", 587, "u", tmp_path / "missing")

    with pytest.raises(FileNotFoundError):
        mailer.send(EmailMessage())

    assert fake_smtp.instances == []
