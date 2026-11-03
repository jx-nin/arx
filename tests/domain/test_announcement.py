import pytest

from arx.domain.announcement import check_category


@pytest.mark.req("FR-ING-02")
@pytest.mark.parametrize(
    "category",
    ["cs.LG", "astro-ph.HE", "physics.plasm-ph", "cond-mat.mtrl-sci", "hep-th", "cs"],
)
def test_accepts_arxiv_categories(category: str) -> None:
    assert check_category(category) == category


@pytest.mark.req("FR-ING-02")
@pytest.mark.parametrize(
    "category", ["", "cs.LG/../api", "cs.LG?x=1", "cs.LG+math.ST", " cs.LG", "CS.LG"]
)
def test_rejects_anything_else(category: str) -> None:
    with pytest.raises(ValueError, match="not an arXiv category"):
        check_category(category)
