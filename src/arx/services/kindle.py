"""Send-to-Kindle use case: fetch a paper by ID or URL, convert and mail it."""

from typing import Protocol

from arx.domain.arxiv_id import parse_reference
from arx.domain.paper import Paper
from arx.services.conversion import ConversionService
from arx.services.delivery import DeliveryService


class PaperSource(Protocol):
    """Looks up papers and their HTML renditions on arXiv (spec 6.6.1)."""

    def paper(self, arxiv_id: str, version: int | None) -> Paper | None:
        """Look up a paper's metadata.

        :param arxiv_id: arXiv identifier without version suffix.
        :param version: Version to look up, or ``None`` for the latest.
        :returns: The paper, or ``None`` if arXiv has no such paper.
        :raises Exception: Adapter-specific request errors, passed through.
        """
        ...

    def html(self, paper: Paper) -> str | None:
        """Download the HTML rendition of the paper's version.

        :param paper: Paper whose rendition to fetch.
        :returns: The HTML page, or ``None`` if arXiv has no rendition.
        :raises Exception: Adapter-specific request errors, passed through.
        """
        ...


class PaperNotFoundError(ValueError):
    """arXiv has no paper with the given ID and version."""


class HtmlUnavailableError(ValueError):
    """arXiv has no HTML rendition of the paper; the PDF path is FR-CNV-05."""


class KindleService:
    """Sends a paper named by ID or URL to the Kindle in one action."""

    def __init__(
        self,
        source: PaperSource,
        conversion: ConversionService,
        delivery: DeliveryService,
    ) -> None:
        """Create the service.

        :param source: Source of paper metadata and HTML renditions.
        :param conversion: Service that converts the rendition to EPUB.
        :param delivery: Service that mails the EPUB.
        """
        self._source = source
        self._conversion = conversion
        self._delivery = delivery

    def send(self, reference: str, recipient: str) -> None:
        """Fetch, convert and mail one paper (FR-ING-04, FR-DLV-01).

        :param reference: arXiv ID or abstract, PDF or HTML URL.
        :param recipient: Kindle address to send to.
        :raises ValueError: If the reference names no paper.
        :raises RecipientNotAllowedError: If the recipient is not allowlisted;
            checked before any request.
        :raises PaperNotFoundError: If arXiv has no such paper.
        :raises HtmlUnavailableError: If the paper has no HTML rendition.
        :raises Exception: Errors from the source, conversion or delivery,
            passed through.
        """
        ref = parse_reference(reference)
        self._delivery.check_recipient(recipient)
        paper = self._source.paper(ref.arxiv_id, ref.version)
        if paper is None:
            version = "" if ref.version is None else f"v{ref.version}"
            raise PaperNotFoundError(f"arXiv has no paper {ref.arxiv_id}{version}")
        html = self._source.html(paper)
        if html is None:
            raise HtmlUnavailableError(
                f"arXiv has no HTML rendition of {paper.arxiv_id}v{paper.version}"
            )
        epub = self._conversion.convert_html(paper, html)
        self._delivery.send_epub(paper, epub, recipient)
