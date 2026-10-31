from pathlib import Path

import pytest

from arx.adapters.conversion.html_cleaner import LatexmlHtmlCleaner

FIXTURE = Path(__file__).parents[2] / "fixtures" / "conversion" / "arxiv_minimal.html"


def article() -> str:
    return LatexmlHtmlCleaner().article(FIXTURE.read_text())


@pytest.mark.req("FR-CNV-01")
def test_returns_the_article_element() -> None:
    assert article().startswith("<article")


@pytest.mark.req("FR-CNV-01")
@pytest.mark.parametrize(
    "expected",
    [
        "1 Introduction",
        "Long documents strain dense attention.",
        "2 Method",
        "We keep the top-k keys per query.",
    ],
)
def test_keeps_article_content(expected: str) -> None:
    assert expected in article()


@pytest.mark.req("FR-CNV-01")
@pytest.mark.parametrize(
    "chrome",
    [
        "Toggle dark mode",
        "Report Issue",
        "Navigation sidebar",
        "arXiv footer",
        "window.reportIssue",
    ],
)
def test_drops_arxiv_page_chrome(chrome: str) -> None:
    assert chrome not in article()


@pytest.mark.req("FR-CNV-01")
@pytest.mark.parametrize(
    "front_matter",
    [
        "Sparse Attention for Long Documents",
        "Ada Lovelace, Alan Turing",
        "We study sparse attention.",
    ],
)
def test_drops_front_matter_the_title_page_repeats(front_matter: str) -> None:
    assert front_matter not in article()


@pytest.mark.req("FR-CNV-01")
@pytest.mark.parametrize(
    "html", ["<html><body><p>Error 404</p></body></html>", "", "  \n"]
)
def test_rejects_html_without_an_article(html: str) -> None:
    with pytest.raises(ValueError, match="<article>"):
        LatexmlHtmlCleaner().article(html)
