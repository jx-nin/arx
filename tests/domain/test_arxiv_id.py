import pytest

from arx.domain.arxiv_id import PaperRef, parse_reference


@pytest.mark.req("FR-ING-04")
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("2401.01234", PaperRef("2401.01234", None)),
        ("2401.01234v2", PaperRef("2401.01234", 2)),
        ("arXiv:2401.01234v2", PaperRef("2401.01234", 2)),
        ("https://arxiv.org/abs/2401.01234", PaperRef("2401.01234", None)),
        ("https://arxiv.org/abs/2401.01234v2", PaperRef("2401.01234", 2)),
        ("https://arxiv.org/pdf/2401.01234v2", PaperRef("2401.01234", 2)),
        ("https://arxiv.org/pdf/2401.01234v2.pdf", PaperRef("2401.01234", 2)),
        ("https://arxiv.org/html/2401.01234v2/", PaperRef("2401.01234", 2)),
        ("http://www.arxiv.org/abs/2401.01234", PaperRef("2401.01234", None)),
        ("arxiv.org/abs/1706.03762", PaperRef("1706.03762", None)),
        ("hep-th/9901001", PaperRef("hep-th/9901001", None)),
        ("https://arxiv.org/abs/math.GT/0309136v1", PaperRef("math.GT/0309136", 1)),
        ("  2401.01234v2\n", PaperRef("2401.01234", 2)),
        ("https://arxiv.org/abs/2401.01234?context=cs", PaperRef("2401.01234", None)),
        ("https://arxiv.org/html/2401.01234v2#S3", PaperRef("2401.01234", 2)),
        ("https://export.arxiv.org/abs/2401.01234v2", PaperRef("2401.01234", 2)),
    ],
)
def test_parses_ids_and_arxiv_urls(text: str, expected: PaperRef) -> None:
    assert parse_reference(text) == expected


@pytest.mark.req("FR-ING-04")
@pytest.mark.parametrize(
    "text",
    [
        "",
        "2401.1",
        "2401.01234v0",
        "https://example.com/abs/2401.01234",
        "https://arxiv.org/list/cs.LG/new",
    ],
)
def test_rejects_text_that_names_no_arxiv_paper(text: str) -> None:
    with pytest.raises(ValueError, match="not an arXiv ID"):
        parse_reference(text)
