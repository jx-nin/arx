import smtplib
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock

import httpx
import pytest

from arx.bootstrap import build_arxiv_client, build_delivery_service
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


@pytest.fixture
def arxiv_requests(monkeypatch: pytest.MonkeyPatch) -> list[httpx.Request]:
    requests: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(404)

    real_client = httpx.Client
    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kwargs: real_client(transport=httpx.MockTransport(respond), **kwargs),
    )
    return requests


@pytest.mark.req("FR-ING-04")
def test_arxiv_requests_identify_arx_and_the_sender_by_default(
    arxiv_requests: list[httpx.Request], tmp_path: Path
) -> None:
    build_arxiv_client(make_settings(tmp_path)).html(PAPER)

    agent = arxiv_requests[0].headers["User-Agent"]
    assert agent.startswith("arx/")
    assert agent.endswith("(mailto:arx.sender@gmail.com)")


@pytest.mark.req("FR-ING-04")
def test_arxiv_user_agent_can_be_configured(
    arxiv_requests: list[httpx.Request], tmp_path: Path
) -> None:
    settings = make_settings(tmp_path, arxiv_user_agent="arx-test (me@example.com)")

    build_arxiv_client(settings).html(PAPER)

    assert arxiv_requests[0].headers["User-Agent"] == "arx-test (me@example.com)"
