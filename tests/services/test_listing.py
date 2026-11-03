import pytest

from arx.domain.announcement import Announcement
from arx.services.listing import ListingService


def announced(arxiv_id: str, announce_type: str) -> Announcement:
    return Announcement(
        arxiv_id, 1, f"Paper {arxiv_id}", ("Ada Lovelace",), announce_type
    )


class FakeSource:
    def __init__(self, announcements: list[Announcement]) -> None:
        self._announcements = announcements
        self.categories: list[str] = []

    def announcements(self, category: str) -> list[Announcement]:
        self.categories.append(category)
        return self._announcements


@pytest.mark.req("FR-ING-02")
def test_today_lists_new_papers_and_cross_lists_without_replacements() -> None:
    source = FakeSource(
        [
            announced("2611.00001", "new"),
            announced("2611.00002", "cross"),
            announced("2303.00003", "replace"),
            announced("1903.00004", "replace-cross"),
        ]
    )

    papers = ListingService(source).today("cs.LG")

    assert [(p.arxiv_id, p.announce_type) for p in papers] == [
        ("2611.00001", "new"),
        ("2611.00002", "cross"),
    ]
    assert source.categories == ["cs.LG"]


@pytest.mark.req("FR-ING-02")
def test_today_checks_the_category_before_any_request() -> None:
    source = FakeSource([])

    with pytest.raises(ValueError, match="not an arXiv category"):
        ListingService(source).today("cs.LG/../api")

    assert source.categories == []
