"""Papers announced in arXiv's daily listing of a category (FR-ING-02)."""

import re
from dataclasses import dataclass

# Archive with optional subject class: cs, hep-th, cs.LG, cond-mat.mtrl-sci.
CATEGORY = re.compile(r"[a-z]+(?:-[a-z]+)?(?:\.[A-Za-z]+(?:-[a-z]+)?)?")


@dataclass(frozen=True)
class Announcement:
    """One paper version in a category's daily listing.

    :param arxiv_id: arXiv identifier without version suffix.
    :param version: Version number announced.
    :param title: Paper title as plain text.
    :param authors: Author names in listing order, without affiliations.
    :param announce_type: arXiv's announce type: ``new``, ``cross`` (listed
        here from another primary category), ``replace`` or ``replace-cross``.
    """

    arxiv_id: str
    version: int
    title: str
    authors: tuple[str, ...]
    announce_type: str


def check_category(text: str) -> str:
    """Check that the text is an arXiv category such as ``cs.LG``.

    :param text: Category as typed.
    :returns: The category, unchanged.
    :raises ValueError: If the text is not an archive or archive.subject code.
    """
    if CATEGORY.fullmatch(text) is None:
        raise ValueError(f"{text!r} is not an arXiv category such as cs.LG")
    return text
