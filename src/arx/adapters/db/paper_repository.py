"""Paper repository on PostgreSQL: one row per arXiv ID (spec 6.2.2).

Synchronous like the M0 services and Alembic; moves to the async engine with
the worker (M1).
"""

from typing import Any

from sqlalchemy import Engine, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from arx.adapters.db.models import PaperRow
from arx.domain.paper import Paper


class PaperRepository:
    """Stores the latest known version of each paper (FR-ING-03, FR-ING-07)."""

    def __init__(self, engine: Engine) -> None:
        """Create the repository.

        :param engine: Engine of a database migrated to the current head.
        """
        self._engine = engine

    def upsert(self, paper: Paper) -> None:
        """Store a paper unless the same or a newer version is already stored.

        A newer version resets the HTML availability, which is per version.
        Each call commits on its own.

        :param paper: Paper to store.
        :raises sqlalchemy.exc.SQLAlchemyError: If the database rejects it.
        """
        values = _to_row(paper)
        statement = insert(PaperRow).values(values)
        newer = {key: value for key, value in values.items() if key != "arxiv_id"}
        newer |= {"html_status": "unknown", "html_checked_at": None}
        statement = statement.on_conflict_do_update(
            index_elements=[PaperRow.arxiv_id],
            set_=newer,
            where=PaperRow.latest_version < statement.excluded.latest_version,
        )
        with self._engine.begin() as connection:
            connection.execute(statement)

    def get(self, arxiv_id: str) -> Paper | None:
        """Look up the stored version of a paper.

        :param arxiv_id: arXiv identifier without version suffix.
        :returns: The paper at its latest stored version, or ``None``.
        :raises sqlalchemy.exc.SQLAlchemyError: If the query fails.
        """
        query = select(PaperRow).where(PaperRow.arxiv_id == arxiv_id)
        with Session(self._engine) as session:
            row = session.scalars(query).one_or_none()
            return None if row is None else _to_paper(row)


def _to_row(paper: Paper) -> dict[str, Any]:
    """Map a paper to the ``paper`` columns it fills.

    :param paper: Paper to map.
    :returns: Column values by name.
    """
    return {
        "arxiv_id": paper.arxiv_id,
        "latest_version": paper.version,
        "title": paper.title,
        # Affiliations follow with a metadata source that has them.
        "authors": [{"name": name, "affiliation": None} for name in paper.authors],
        "abstract": paper.abstract,
        "license": paper.license,
        "published_at": paper.published_at,
        "updated_at": paper.updated_at,
    }


def _to_paper(row: PaperRow) -> Paper:
    """Map a ``paper`` row back to the domain entity.

    :param row: Loaded ``paper`` row.
    :returns: The paper at the row's latest version.
    """
    return Paper(
        arxiv_id=row.arxiv_id,
        version=row.latest_version,
        title=row.title,
        authors=tuple(author["name"] for author in row.authors),
        abstract=row.abstract,
        published_at=row.published_at,
        updated_at=row.updated_at,
        license=row.license,
    )
