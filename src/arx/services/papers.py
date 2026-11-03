"""Paper storage port: the papers Arx knows, one per arXiv ID (spec 6.2.2)."""

from typing import Protocol

from arx.domain.paper import Paper


class PaperStore(Protocol):
    """Keeps the latest known version of each paper (FR-ING-03, FR-ING-07)."""

    def upsert(self, paper: Paper) -> None:
        """Store a paper unless a newer version of it is already stored.

        Storing the same version again changes nothing, so harvests can rerun.

        :param paper: Paper to store.
        :raises Exception: Adapter-specific storage errors, passed through.
        """
        ...

    def get(self, arxiv_id: str) -> Paper | None:
        """Look up the stored version of a paper.

        :param arxiv_id: arXiv identifier without version suffix.
        :returns: The paper at its latest stored version, or ``None``.
        :raises Exception: Adapter-specific storage errors, passed through.
        """
        ...
