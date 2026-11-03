"""SQLAlchemy models of the tables the migrations create (spec 6.2.2).

The migrations in ``migrations/`` are the source of the schema; these models
must describe the same tables, which an integration test checks.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Computed,
    DateTime,
    Identity,
    Index,
    SmallInteger,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

SEARCH_TSV = (
    "setweight(to_tsvector('english', title), 'A') || "
    "setweight(to_tsvector('english', abstract), 'B')"
)


class Base(DeclarativeBase):
    """Declarative base whose metadata holds every Arx table."""


class PaperRow(Base):
    """One arXiv paper at its latest known version (``paper`` table).

    ``primary_category`` is nullable until the harvest fills it (spec 6.2.2).
    """

    __tablename__ = "paper"
    __table_args__ = (
        CheckConstraint(
            "html_status IN ('unknown','available','unavailable')",
            name="paper_html_status_check",
        ),
        Index("paper_search_idx", "search_tsv", postgresql_using="gin"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    arxiv_id: Mapped[str] = mapped_column(Text, unique=True)
    latest_version: Mapped[int] = mapped_column(SmallInteger)
    title: Mapped[str] = mapped_column(Text)
    authors: Mapped[list[dict[str, Any]]] = mapped_column(JSONB)
    abstract: Mapped[str] = mapped_column(Text)
    primary_category: Mapped[str | None] = mapped_column(Text)
    doi: Mapped[str | None] = mapped_column(Text)
    journal_ref: Mapped[str | None] = mapped_column(Text)
    license: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    html_status: Mapped[str] = mapped_column(Text, server_default="unknown")
    html_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    search_tsv: Mapped[str | None] = mapped_column(
        TSVECTOR, Computed(SEARCH_TSV, persisted=True)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


Index("paper_published_idx", PaperRow.published_at.desc())
