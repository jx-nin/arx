"""Daily listing use case: the papers arXiv announced today in one category."""

from typing import Protocol

from arx.domain.announcement import Announcement, check_category

# Replacements are new versions of older papers, not new reading.
LISTED_TYPES = frozenset({"new", "cross"})


class ListingSource(Protocol):
    """Reads arXiv's latest daily announcement of a category (spec 6.6.1)."""

    def announcements(self, category: str) -> list[Announcement]:
        """Read the category's latest announcement.

        :param category: arXiv category such as ``cs.LG``, already checked.
        :returns: Every announced paper version, in listing order.
        :raises Exception: Adapter-specific request errors, passed through.
        """
        ...


class ListingService:
    """Lists the latest announced papers of one category (FR-ING-02, manual)."""

    def __init__(self, source: ListingSource) -> None:
        """Create the service.

        :param source: Source of the daily announcement.
        """
        self._source = source

    def today(self, category: str) -> list[Announcement]:
        """List new papers and cross-lists of the latest announcement.

        :param category: arXiv category such as ``cs.LG``.
        :returns: New and cross-listed papers in listing order, without
            replacements; empty on days without announcement.
        :raises ValueError: If the text is not an arXiv category; checked
            before any request.
        :raises Exception: Errors from the source, passed through.
        """
        announcements = self._source.announcements(check_category(category))
        return [a for a in announcements if a.announce_type in LISTED_TYPES]
