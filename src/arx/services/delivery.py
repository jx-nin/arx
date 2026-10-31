"""Delivery use case: e-mail a converted EPUB to a Kindle (spec 6.6.3)."""

import logging
import re
import unicodedata
from email.message import EmailMessage
from typing import Protocol

from arx.domain.paper import Paper

logger = logging.getLogger(__name__)

FILENAME_MAX_CHARS = 80
TITLE_WORDS = 5


class Mailer(Protocol):
    """Submits e-mail to the approved sender's SMTP relay."""

    def send(self, message: EmailMessage) -> None:
        """Send a complete message.

        :param message: Message with sender, recipient and attachment set.
        :raises Exception: Adapter-specific transport errors, passed through
            until FR-DLV-06 classifies them for retries.
        """
        ...


class RecipientNotAllowedError(ValueError):
    """The recipient is not on the delivery allowlist (FR-DLV-07)."""


class AttachmentTooLargeError(ValueError):
    """The file exceeds the raw attachment size limit (FR-DLV-03).

    :param size: File size in bytes.
    :param limit: Configured limit in bytes.
    """

    def __init__(self, size: int, limit: int) -> None:
        """Create the error with a message that names both sizes.

        :param size: File size in bytes.
        :param limit: Configured limit in bytes.
        """
        super().__init__(
            f"EPUB is {size} bytes, over the {limit}-byte attachment limit; "
            "it was not sent"
        )
        self.size = size
        self.limit = limit


class DeliveryService:
    """Sends converted papers to allowlisted Kindle addresses by e-mail."""

    def __init__(
        self,
        mailer: Mailer,
        sender: str,
        allowed_recipients: frozenset[str],
        max_bytes: int,
    ) -> None:
        """Create the service.

        :param mailer: Mailer that submits the message.
        :param sender: Approved sender address (FR-DLV-02).
        :param allowed_recipients: Addresses delivery may send to, any case.
        :param max_bytes: Raw attachment size limit in bytes.
        """
        self._mailer = mailer
        self._sender = sender
        self._allowed_recipients = frozenset(r.lower() for r in allowed_recipients)
        self._max_bytes = max_bytes

    def send_epub(self, paper: Paper, epub: bytes, recipient: str) -> None:
        """E-mail one paper's EPUB as an attachment (FR-DLV-02).

        Checks the recipient (FR-DLV-07) and the file size (FR-DLV-03) before
        anything is sent.

        :param paper: Paper the EPUB was converted from.
        :param epub: The EPUB file contents.
        :param recipient: Kindle address to send to.
        :raises RecipientNotAllowedError: If the recipient is not allowlisted.
        :raises AttachmentTooLargeError: If the EPUB exceeds the size limit.
        :raises Exception: Transport errors from the mailer, passed through.
        """
        if recipient.lower() not in self._allowed_recipients:
            raise RecipientNotAllowedError(f"{recipient} is not an allowed recipient")
        if len(epub) > self._max_bytes:
            raise AttachmentTooLargeError(len(epub), self._max_bytes)

        # arXiv titles can wrap; header values must be one line.
        title = " ".join(paper.title.split())
        message = EmailMessage()
        message["From"] = self._sender
        message["To"] = recipient
        message["Subject"] = title
        message.set_content(f"{title}\narXiv:{paper.arxiv_id}v{paper.version}\n")
        message.add_attachment(
            epub,
            maintype="application",
            subtype="epub+zip",
            filename=_attachment_filename(paper),
        )
        self._mailer.send(message)
        # The Kindle address is an abuse target (spec 7.2 T9); keep it out of logs.
        logger.info("Sent %s (%d bytes)", paper.arxiv_id, len(epub))


def _attachment_filename(paper: Paper) -> str:
    """Name the attachment ``<first-author>-<year>-<short-title>.epub`` (spec 6.6.3).

    :param paper: Paper the attachment holds.
    :returns: An ASCII file name of at most :data:`FILENAME_MAX_CHARS` characters;
        the versioned arXiv ID stands in for an author name without ASCII letters.
        The surname is the name's last word, so suffixes such as ``Jr.`` win.
    """
    name = paper.authors[0].split() if paper.authors else []
    surname = _slug_words(name[-1]) if name else []
    first = surname or [f"{paper.arxiv_id}v{paper.version}".replace("/", "-")]
    title = _slug_words(paper.title)[:TITLE_WORDS]
    stem = "-".join([*first, str(paper.published_at.year), *title])
    suffix = ".epub"
    return stem[: FILENAME_MAX_CHARS - len(suffix)].rstrip("-") + suffix


def _slug_words(text: str) -> list[str]:
    """Split text into lower-case ASCII words, dropping accents and punctuation.

    :param text: Any Unicode text.
    :returns: The ASCII letter and digit runs of ``text``.
    """
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.findall(r"[a-z0-9]+", ascii_text.lower())
