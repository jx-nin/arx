from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine
from testcontainers.community.postgres import PostgresContainer

from arx.bootstrap import build_engine
from arx.settings import DatabaseSettings

ROOT = Path(__file__).parents[3]
# Same image as compose.yaml.
POSTGRES_IMAGE = "pgvector/pgvector:pg17"


@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    with PostgresContainer(POSTGRES_IMAGE, driver=None) as postgres:
        yield postgres.get_connection_url()


@pytest.fixture
def alembic_config(
    database_url: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Config:
    url_file = tmp_path / "database_url"
    url_file.write_text(f"{database_url}\n")
    monkeypatch.setenv("ARX_DATABASE_URL_FILE", str(url_file))
    return Config(toml_file=ROOT / "pyproject.toml")


@pytest.fixture
def engine(alembic_config: Config) -> Iterator[Engine]:
    command.upgrade(alembic_config, "head")
    engine = build_engine(DatabaseSettings(_env_file=None))  # type: ignore[call-arg]
    yield engine
    engine.dispose()
    command.downgrade(alembic_config, "base")
