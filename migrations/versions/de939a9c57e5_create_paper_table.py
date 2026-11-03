"""Create the paper table (spec 6.2.2).

The pgvector extension follows with the first table that has an embedding.

Revision ID: de939a9c57e5
Revises:
Create Date: 2026-11-03 20:51:09.237959
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "de939a9c57e5"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "paper",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("arxiv_id", sa.Text(), nullable=False),
        sa.Column("latest_version", sa.SmallInteger(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("authors", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("abstract", sa.Text(), nullable=False),
        # Nullable until the harvest fills it; arx kindle and arx send do not know it.
        sa.Column("primary_category", sa.Text(), nullable=True),
        sa.Column("doi", sa.Text(), nullable=True),
        sa.Column("journal_ref", sa.Text(), nullable=True),
        sa.Column("license", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("html_status", sa.Text(), server_default="unknown", nullable=False),
        sa.Column("html_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "search_tsv",
            postgresql.TSVECTOR(),
            sa.Computed(
                "setweight(to_tsvector('english', title), 'A') || "
                "setweight(to_tsvector('english', abstract), 'B')",
                persisted=True,
            ),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "html_status IN ('unknown','available','unavailable')",
            name="paper_html_status_check",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("arxiv_id"),
    )
    op.create_index(
        "paper_published_idx",
        "paper",
        [sa.literal_column("published_at DESC")],
        unique=False,
    )
    op.create_index(
        "paper_search_idx",
        "paper",
        ["search_tsv"],
        unique=False,
        postgresql_using="gin",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("paper_search_idx", table_name="paper", postgresql_using="gin")
    op.drop_index("paper_published_idx", table_name="paper")
    op.drop_table("paper")
