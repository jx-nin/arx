"""Alembic environment: migrates the database named by ``ARX_DATABASE_URL_FILE``."""

import logging

from alembic import context

from arx.adapters.db.models import Base
from arx.bootstrap import build_engine
from arx.settings import DatabaseSettings

if context.is_offline_mode():
    raise SystemExit("Offline mode (--sql) is not supported; run against a database.")

# Entry point of the alembic CLI: show which revisions run. No-op under pytest.
logging.basicConfig(format="%(levelname)-5.5s [%(name)s] %(message)s")
logging.getLogger("alembic").setLevel(logging.INFO)

engine = build_engine(DatabaseSettings())
try:
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)
        with context.begin_transaction():
            context.run_migrations()
finally:
    engine.dispose()
