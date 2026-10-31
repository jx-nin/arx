from datetime import UTC, datetime
from email.message import EmailMessage

import pytest

from arx.domain.paper import Paper
from arx.services.delivery import (
    AttachmentTooLargeError,
    DeliveryService,
    RecipientNotAllowedError,
)

SENDER = "arx.sender@gmail.com"
RECIPIENT = "reader@kindle.com"
EPUB = b"PK fake epub"


class FakeMailer:
    def __init__(self) -> None:
        self.messages: list[EmailMessage] = []

    def send(self, message: EmailMessage) -> None:
        self.messages.append(message)


def make_paper(**overrides: object) -> Paper:
    fields: dict[str, object] = {
        "arxiv_id": "2401.01234",
        "version": 2,
        "title": "Sparse Attention for Long Documents",
        "authors": ("Ada Lovelace", "Alan Turing"),
        "abstract": "We study sparse attention.",
        "published_at": datetime(2024, 1, 3, tzinfo=UTC),
        "updated_at": datetime(2024, 2, 14, tzinfo=UTC),
        "license": None,
    }
    fields.update(overrides)
    return Paper(**fields)  # type: ignore[arg-type]


def make_service(mailer: FakeMailer, max_bytes: int = 1000) -> DeliveryService:
    return DeliveryService(mailer, SENDER, frozenset({RECIPIENT}), max_bytes)


def send(paper: Paper | None = None) -> EmailMessage:
    mailer = FakeMailer()
    make_service(mailer).send_epub(paper or make_paper(), EPUB, RECIPIENT)
    [message] = mailer.messages
    return message


def attachment_name(message: EmailMessage) -> str | None:
    [attachment] = message.iter_attachments()
    return attachment.get_filename()


@pytest.mark.req("FR-DLV-02")
def test_mails_the_epub_from_the_approved_sender_to_the_kindle() -> None:
    message = send()

    [attachment] = message.iter_attachments()
    assert message["From"] == SENDER
    assert message["To"] == RECIPIENT
    assert message["Subject"] == "Sparse Attention for Long Documents"
    assert attachment.get_content_type() == "application/epub+zip"
    assert attachment.get_content() == EPUB


@pytest.mark.req("FR-DLV-02")
def test_plain_text_body_names_the_paper() -> None:
    body = send().get_body(("plain",))

    assert body is not None
    text = body.get_content()
    assert "Sparse Attention for Long Documents" in text
    assert "arXiv:2401.01234v2" in text


@pytest.mark.req("FR-DLV-02")
def test_attachment_is_named_after_first_author_year_and_short_title() -> None:
    assert (
        attachment_name(send())
        == "lovelace-2024-sparse-attention-for-long-documents.epub"
    )


@pytest.mark.req("FR-DLV-02")
def test_attachment_name_is_ascii_safe() -> None:
    paper = make_paper(
        authors=("Paul Erdős",), title="Über <k>-Färbungen: ein Überblick, Teil 2"
    )

    assert (
        attachment_name(send(paper)) == "erdos-2024-uber-k-farbungen-ein-uberblick.epub"
    )


@pytest.mark.req("FR-DLV-02")
def test_attachment_name_is_capped_at_80_characters() -> None:
    name = attachment_name(send(make_paper(title="Supercalifragilistic " * 20)))

    assert name is not None
    assert len(name) <= 80
    assert name.endswith(".epub")
    assert not name.removesuffix(".epub").endswith("-")


@pytest.mark.req("FR-DLV-02")
def test_attachment_name_falls_back_to_the_arxiv_id() -> None:
    paper = make_paper(authors=(), title="变分推断")

    assert attachment_name(send(paper)) == "2401.01234v2-2024.epub"


@pytest.mark.req("FR-DLV-02")
def test_attachment_name_survives_a_blank_author_name() -> None:
    paper = make_paper(authors=(" ",), title="Sparse Attention")

    assert attachment_name(send(paper)) == "2401.01234v2-2024-sparse-attention.epub"


@pytest.mark.req("FR-DLV-02")
def test_attachment_name_keeps_a_hyphenated_surname() -> None:
    paper = make_paper(authors=("Mary Smith-Jones",), title="Sparse Attention")

    assert attachment_name(send(paper)) == "smith-jones-2024-sparse-attention.epub"


@pytest.mark.req("FR-DLV-02")
def test_attachment_name_fallback_has_no_slash_for_old_style_ids() -> None:
    paper = make_paper(arxiv_id="hep-th/9901001", authors=(), title="")

    assert attachment_name(send(paper)) == "hep-th-9901001v2-2024.epub"


@pytest.mark.req("FR-DLV-02")
def test_wrapped_title_becomes_a_one_line_subject() -> None:
    message = send(make_paper(title="Sparse Attention\n  for Long Documents"))

    assert message["Subject"] == "Sparse Attention for Long Documents"


@pytest.mark.req("FR-DLV-07")
def test_recipient_match_ignores_case() -> None:
    mailer = FakeMailer()

    make_service(mailer).send_epub(make_paper(), EPUB, "Reader@Kindle.COM")

    assert len(mailer.messages) == 1


@pytest.mark.req("FR-DLV-07")
def test_rejects_recipient_outside_the_allowlist_without_sending() -> None:
    mailer = FakeMailer()

    with pytest.raises(RecipientNotAllowedError, match=r"stranger@kindle\.com"):
        make_service(mailer).send_epub(make_paper(), EPUB, "stranger@kindle.com")

    assert mailer.messages == []


@pytest.mark.req("FR-DLV-03")
def test_sends_a_file_exactly_at_the_limit() -> None:
    mailer = FakeMailer()

    make_service(mailer, max_bytes=len(EPUB)).send_epub(make_paper(), EPUB, RECIPIENT)

    assert len(mailer.messages) == 1


@pytest.mark.req("FR-DLV-03")
def test_rejects_a_file_over_the_limit_without_sending() -> None:
    mailer = FakeMailer()
    service = make_service(mailer, max_bytes=len(EPUB) - 1)

    with pytest.raises(AttachmentTooLargeError) as error:
        service.send_epub(make_paper(), EPUB, RECIPIENT)

    assert mailer.messages == []
    assert error.value.size == len(EPUB)
    assert error.value.limit == len(EPUB) - 1
    assert f"{len(EPUB)} bytes" in str(error.value)
