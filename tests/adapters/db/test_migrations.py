import pytest
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import Engine, inspect

from arx.adapters.db.models import Base

pytestmark = pytest.mark.integration


def test_upgrade_builds_the_schema_the_models_describe(engine: Engine) -> None:
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        differences = compare_metadata(context, Base.metadata)

    assert "paper" in inspect(engine).get_table_names()
    assert differences == []
