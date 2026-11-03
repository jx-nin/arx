---
type: Component
title: Paper store and migrations
description: PostgreSQL `paper` table created by the first Alembic migration, and the repository that stores each paper once at its latest version.
tags: [database, ingestion, migrations]
status: draft
generated: { by: "agent:claude-opus-5-5", at: 2026-11-03T00:00:00Z }
---

# Component

* Covers FR-ING-03 (idempotent upsert; the harvest follows in M1) and FR-ING-07 (one row per arXiv ID) for M0 (spec 6.2.2). Not wired into `arx kindle` yet.
* `migrations/`: Alembic, configured under `[tool.alembic]` in `pyproject.toml`. The first revision creates only `paper`; `primary_category` is nullable until the harvest fills it, and the pgvector extension ([ADR-003](/decisions/adr-003-pgvector.md)) comes with the first embedding table. Offline mode (`--sql`) is refused.
* `settings.py`: `DatabaseSettings` reads `ARX_DATABASE_URL_FILE` (default `/run/secrets/database_url`), apart from the delivery settings so neither side needs the other's variables; both read one `.env` and ignore unknown `ARX_*` keys.
* `bootstrap.py`: `build_engine` reads the URL file and always selects the psycopg 3 driver ([database driver](/decisions/db-driver.md)); Alembic's `env.py` uses it.
* `services/papers.py`: `PaperStore` protocol (`upsert`, `get`).
* `adapters/db/models.py`: SQLAlchemy models mirroring the migrations; an integration test compares them with the migrated schema.
* `adapters/db/paper_repository.py`: `PaperRepository` upserts on `arxiv_id` and replaces a row only with a newer version, resetting `html_status` (availability is per version); each call commits on its own. Synchronous like the M0 services until the async worker (M1).
* Tests: `tests/adapters/db/` (`integration`), on the `pgvector/pgvector:pg17` image from `compose.yaml` via testcontainers ([test layout](/decisions/test-layout.md)).
