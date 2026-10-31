"""Paper entity: the arXiv metadata of one paper version."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Paper:
    """An arXiv paper at one version, mirroring the ``paper`` table (spec 6.2.2).

    :param arxiv_id: arXiv identifier without version suffix, e.g. ``2401.01234``.
    :param version: Version number, e.g. ``2`` for ``2401.01234v2``.
    :param title: Paper title as plain text.
    :param authors: Author names in listing order.
    :param abstract: Abstract as plain text.
    :param published_at: When the first version was published.
    :param updated_at: When this version was published.
    :param license: Licence URL, or ``None`` when arXiv lists none.
    """

    arxiv_id: str
    version: int
    title: str
    authors: tuple[str, ...]
    abstract: str
    published_at: datetime
    updated_at: datetime
    license: str | None
