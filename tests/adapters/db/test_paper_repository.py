from dataclasses import replace
from datetime import UTC, datetime

import pytest
from sqlalchemy import Engine, func, select, update

from arx.adapters.db.models import PaperRow
from arx.adapters.db.paper_repository import PaperRepository
from arx.domain.paper import Paper
from arx.services.papers import PaperStore

pytestmark = pytest.mark.integration

V1 = Paper(
    arxiv_id="2401.01234",
    version=1,
    title="Sparse Attention for Long Documents",
    authors=("Ada Lovelace", "Charles Babbage"),
    abstract="We attend sparsely.",
    published_at=datetime(2024, 1, 3, 18, 0, tzinfo=UTC),
    updated_at=datetime(2024, 1, 3, 18, 0, tzinfo=UTC),
    license="http://creativecommons.org/licenses/by/4.0/",
)
V2 = replace(
    V1,
    version=2,
    title="Sparse Attention for Very Long Documents",
    updated_at=datetime(2024, 2, 1, 9, 30, tzinfo=UTC),
)


@pytest.fixture
def store(engine: Engine) -> PaperStore:
    return PaperRepository(engine)


def count_rows(engine: Engine) -> int:
    with engine.connect() as connection:
        return connection.scalar(select(func.count()).select_from(PaperRow)) or 0


def test_a_stored_paper_reads_back_unchanged(store: PaperStore) -> None:
    store.upsert(V1)

    assert store.get("2401.01234") == V1


def test_an_unknown_paper_is_none(store: PaperStore) -> None:
    assert store.get("2401.99999") is None


@pytest.mark.req("FR-ING-03")
@pytest.mark.req("FR-ING-07")
def test_storing_the_same_paper_again_keeps_one_row(
    store: PaperStore, engine: Engine
) -> None:
    store.upsert(V1)
    store.upsert(V1)

    assert count_rows(engine) == 1
    assert store.get("2401.01234") == V1


@pytest.mark.req("FR-ING-03")
def test_a_newer_version_replaces_the_older(store: PaperStore, engine: Engine) -> None:
    store.upsert(V1)
    store.upsert(V2)

    assert count_rows(engine) == 1
    assert store.get("2401.01234") == V2


@pytest.mark.req("FR-ING-03")
def test_an_older_version_does_not_overwrite_the_newer(store: PaperStore) -> None:
    store.upsert(V2)
    store.upsert(V1)

    assert store.get("2401.01234") == V2


@pytest.mark.req("FR-ING-03")
def test_a_newer_version_keeps_the_doi_and_resets_html_availability(
    store: PaperStore, engine: Engine
) -> None:
    store.upsert(V1)
    with engine.begin() as connection:
        connection.execute(
            update(PaperRow).values(
                doi="10.1000/xyz",
                html_status="available",
                html_checked_at=datetime(2024, 1, 4, tzinfo=UTC),
            )
        )

    store.upsert(V2)

    with engine.connect() as connection:
        row = connection.execute(
            select(PaperRow.doi, PaperRow.html_status, PaperRow.html_checked_at)
        ).one()
    assert tuple(row) == ("10.1000/xyz", "unknown", None)
