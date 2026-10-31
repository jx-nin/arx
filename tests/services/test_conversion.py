import re
import zipfile
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path

import pytest

from arx.adapters.conversion.epub_builder import PandocEpubBuilder
from arx.adapters.conversion.html_cleaner import LatexmlHtmlCleaner
from arx.domain.paper import Paper
from arx.services.conversion import ConversionService

FIXTURE = Path(__file__).parents[1] / "fixtures" / "conversion" / "arxiv_minimal.html"
SOURCE = "<html><body>arXiv page</body></html>"
ARTICLE = "<article><h2>1 Introduction</h2></article>"
EPUB = b"PK fake epub"


class FakeHtmlCleaner:
    def __init__(self) -> None:
        self.html: str | None = None

    def article(self, html: str) -> str:
        self.html = html
        return ARTICLE


class FakeEpubBuilder:
    def __init__(self) -> None:
        self.html: str | None = None
        self.paper: Paper | None = None

    def build(self, html: str, paper: Paper) -> bytes:
        self.html = html
        self.paper = paper
        return EPUB


def make_paper(**overrides: object) -> Paper:
    fields: dict[str, object] = {
        "arxiv_id": "2401.01234",
        "version": 2,
        "title": "Sparse Attention for Long Documents",
        "authors": ("Ada Lovelace", "Alan Turing"),
        "abstract": "We study sparse attention.",
        "published_at": datetime(2024, 1, 3, tzinfo=UTC),
        "updated_at": datetime(2024, 2, 14, tzinfo=UTC),
        "license": "http://creativecommons.org/licenses/by/4.0/",
    }
    fields.update(overrides)
    return Paper(**fields)  # type: ignore[arg-type]


def convert(paper: Paper) -> str:
    builder = FakeEpubBuilder()
    ConversionService(FakeHtmlCleaner(), builder).convert_html(paper, SOURCE)
    assert builder.html is not None
    return builder.html


@pytest.mark.req("FR-CNV-01")
def test_builds_the_cleaned_article_into_an_epub_for_the_paper() -> None:
    cleaner = FakeHtmlCleaner()
    builder = FakeEpubBuilder()
    paper = make_paper()

    epub = ConversionService(cleaner, builder).convert_html(paper, SOURCE)

    assert epub == EPUB
    assert cleaner.html == SOURCE
    assert builder.paper == paper
    assert builder.html is not None and ARTICLE in builder.html


@pytest.mark.req("FR-CNV-01")
@pytest.mark.parametrize(
    "expected",
    [
        "Sparse Attention for Long Documents",
        "Ada Lovelace, Alan Turing",
        "arXiv:2401.01234v2",
        "2024-01-03",
        "2024-02-14",
        "http://creativecommons.org/licenses/by/4.0/",
        "https://arxiv.org/abs/2401.01234v2",
        "We study sparse attention.",
    ],
)
def test_title_page_shows_paper_metadata_before_the_body(expected: str) -> None:
    html = convert(make_paper())

    assert expected in html
    assert html.index(expected) < html.index(ARTICLE)


@pytest.mark.req("FR-CNV-01")
def test_title_page_escapes_metadata() -> None:
    html = convert(make_paper(title="Bounds for <k> & beyond"))

    assert "Bounds for &lt;k&gt; &amp; beyond" in html
    assert "<k>" not in html


@pytest.mark.req("FR-CNV-01")
def test_title_page_omits_missing_licence() -> None:
    html = convert(make_paper(license=None))

    assert "None" not in html
    assert 'class="license"' not in html


@pytest.mark.req("FR-CNV-01")
def test_title_page_omits_empty_author_list() -> None:
    assert 'class="authors"' not in convert(make_paper(authors=()))


@pytest.mark.req("FR-CNV-01")
def test_converted_paper_has_one_title_page_and_no_duplicate_toc_entries() -> None:
    service = ConversionService(LatexmlHtmlCleaner(), PandocEpubBuilder())
    epub = zipfile.ZipFile(
        BytesIO(service.convert_html(make_paper(), FIXTURE.read_text()))
    )

    toc = re.search(
        r'<nav epub:type="toc".*?</nav>', epub.read("EPUB/nav.xhtml").decode(), re.S
    )
    assert toc
    entries = re.findall(r"<a [^>]*>([^<]*)</a>", toc.group())

    assert not [name for name in epub.namelist() if "title_page" in name]
    assert entries == [make_paper().title, "1 Introduction", "2 Method"]
