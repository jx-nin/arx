from datetime import UTC, datetime
from email.message import EmailMessage

import pytest

from arx.domain.paper import Paper
from arx.services.conversion import ConversionService
from arx.services.delivery import DeliveryService, RecipientNotAllowedError
from arx.services.kindle import HtmlUnavailableError, KindleService, PaperNotFoundError

RECIPIENT = "reader@kindle.com"
PAPER = Paper(
    arxiv_id="2401.01234",
    version=2,
    title="Sparse Attention for Long Documents",
    authors=("Ada Lovelace",),
    abstract="We study sparse attention.",
    published_at=datetime(2024, 1, 3, tzinfo=UTC),
    updated_at=datetime(2024, 2, 14, tzinfo=UTC),
    license=None,
)


class FakeSource:
    def __init__(self, paper: Paper | None = PAPER, html: str | None = "<p>body</p>"):
        self._paper = paper
        self._html = html
        self.lookups: list[tuple[str, int | None]] = []

    def paper(self, arxiv_id: str, version: int | None) -> Paper | None:
        self.lookups.append((arxiv_id, version))
        return self._paper

    def html(self, paper: Paper) -> str | None:
        return self._html


class FakeCleaner:
    def article(self, html: str) -> str:
        return html


class FakeBuilder:
    def build(self, html: str, paper: Paper) -> bytes:
        return f"EPUB {paper.arxiv_id}: {html}".encode()


class FakeMailer:
    def __init__(self) -> None:
        self.messages: list[EmailMessage] = []

    def send(self, message: EmailMessage) -> None:
        self.messages.append(message)


def make_service(source: FakeSource, mailer: FakeMailer) -> KindleService:
    conversion = ConversionService(FakeCleaner(), FakeBuilder())
    delivery = DeliveryService(
        mailer, "arx.sender@gmail.com", frozenset({RECIPIENT}), 10_000
    )
    return KindleService(source, conversion, delivery)


@pytest.mark.req("FR-ING-04")
@pytest.mark.req("FR-DLV-01")
def test_sends_the_converted_paper_named_by_a_url() -> None:
    source, mailer = FakeSource(), FakeMailer()

    make_service(source, mailer).send("https://arxiv.org/abs/2401.01234", RECIPIENT)

    assert source.lookups == [("2401.01234", None)]
    [message] = mailer.messages
    [attachment] = message.iter_attachments()
    epub = attachment.get_content()
    assert message["To"] == RECIPIENT
    assert epub.startswith(b"EPUB 2401.01234:")
    assert b"<p>body</p>" in epub


@pytest.mark.req("FR-ING-04")
def test_looks_up_the_version_the_reference_names() -> None:
    source = FakeSource()

    make_service(source, FakeMailer()).send("2401.01234v2", RECIPIENT)

    assert source.lookups == [("2401.01234", 2)]


@pytest.mark.req("FR-ING-04")
def test_rejects_an_unknown_paper() -> None:
    mailer = FakeMailer()

    with pytest.raises(PaperNotFoundError, match="2401.99999"):
        make_service(FakeSource(paper=None), mailer).send("2401.99999", RECIPIENT)

    assert mailer.messages == []


@pytest.mark.req("FR-ING-04")
def test_rejects_a_paper_without_html_rendition() -> None:
    mailer = FakeMailer()

    with pytest.raises(HtmlUnavailableError, match="2401.01234v2"):
        make_service(FakeSource(html=None), mailer).send("2401.01234", RECIPIENT)

    assert mailer.messages == []


@pytest.mark.req("FR-DLV-07")
def test_checks_the_recipient_before_fetching_anything() -> None:
    source = FakeSource()

    with pytest.raises(RecipientNotAllowedError):
        make_service(source, FakeMailer()).send("2401.01234", "other@kindle.com")

    assert source.lookups == []
