"""Conversion use case: turn a paper's HTML rendition into a Kindle EPUB."""

from html import escape
from typing import Protocol

from arx.domain.paper import Paper


class HtmlCleaner(Protocol):
    """Extracts the paper body from an HTML rendition (spec 6.5.1 step 3)."""

    def article(self, html: str) -> str:
        """Return the article without page chrome or the front matter it repeats.

        :param html: The HTML rendition as served by arXiv.
        :returns: The article markup.
        :raises ValueError: If the HTML has no article.
        """
        ...


class EpubBuilder(Protocol):
    """Builds an EPUB 3 file from prepared HTML (spec 6.5.1 step 9)."""

    def build(self, html: str, paper: Paper) -> bytes:
        """Build an EPUB 3 file with a table of contents and the Kindle stylesheet.

        :param html: Complete HTML document: title page followed by the body.
        :param paper: Paper whose metadata goes into the EPUB package.
        :returns: The EPUB file contents.
        :raises Exception: Adapter-specific build errors, passed through until
            FR-CNV-08 maps them to recorded diagnostics.
        """
        ...


class ConversionService:
    """Converts arXiv HTML renditions to EPUB files for the Kindle."""

    def __init__(self, html_cleaner: HtmlCleaner, epub_builder: EpubBuilder) -> None:
        """Create the service.

        :param html_cleaner: Cleaner that extracts the article from the rendition.
        :param epub_builder: Builder that packages the prepared HTML as EPUB.
        """
        self._html_cleaner = html_cleaner
        self._epub_builder = epub_builder

    def convert_html(self, paper: Paper, html: str) -> bytes:
        """Convert an arXiv HTML rendition to an EPUB (FR-CNV-01).

        Puts a title page in front of the cleaned article and builds the EPUB
        (spec 6.5.1 steps 3, 8 and 9).

        :param paper: Metadata for the title page and the EPUB package.
        :param html: The HTML rendition as served by arXiv.
        :returns: The EPUB file contents from the builder.
        :raises ValueError: If the HTML has no article.
        :raises Exception: Build errors from the EPUB builder, passed through.
        """
        document = (
            '<!DOCTYPE html>\n<html><head><meta charset="utf-8">'
            f"<title>{escape(paper.title)}</title></head><body>\n"
            f"{_title_page(paper)}\n{self._html_cleaner.article(html)}\n"
            "</body></html>\n"
        )
        return self._epub_builder.build(document, paper)


def _title_page(paper: Paper) -> str:
    """Render the title page (spec 6.5.1 step 8).

    :param paper: Paper whose metadata the title page shows.
    :returns: The title page as an HTML ``<section>``.
    """
    versioned_id = f"{paper.arxiv_id}v{paper.version}"
    link = f"https://arxiv.org/abs/{versioned_id}"
    lines = ['<section class="title-page">', f"<h1>{escape(paper.title)}</h1>"]
    if paper.authors:
        lines.append(f'<p class="authors">{escape(", ".join(paper.authors))}</p>')
    lines += [
        f'<p class="arxiv-id">arXiv:{escape(versioned_id)}</p>',
        f'<p class="link"><a href="{escape(link)}">{escape(link)}</a></p>',
        f'<p class="dates">Published {paper.published_at.date().isoformat()}, '
        f"this version {paper.updated_at.date().isoformat()}</p>",
    ]
    if paper.license is not None:
        lines.append(f'<p class="license">Licence: {escape(paper.license)}</p>')
    lines += [
        '<p class="abstract-title">Abstract</p>',
        f'<p class="abstract">{escape(paper.abstract)}</p>',
        "</section>",
    ]
    return "\n".join(lines)
