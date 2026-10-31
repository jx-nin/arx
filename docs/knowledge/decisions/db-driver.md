---
type: Decision
title: Database driver psycopg 3
description: psycopg 3 is the only PostgreSQL driver, async for the app and sync for Alembic and the CLI.
tags: [database, dependencies]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-10-31T00:00:00Z }  # decided by human:jx-nin
---

# Decision

* Answers Q-11 of the [specification](/specs/tds.md) (v0.4): psycopg 3 instead of asyncpg.
* It is already a dependency, and SQLAlchemy 2.0 uses it in both modes (`postgresql+psycopg://`), so the app, Alembic and the CLI share one driver.
* Trade-off: asyncpg is faster on raw throughput, which does not matter for a single-user, rate-limit-bound workload.
