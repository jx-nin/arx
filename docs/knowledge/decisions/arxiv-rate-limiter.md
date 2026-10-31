---
type: Decision
title: arXiv rate limiter placement
description: The arXiv rate limiter lives in the arXiv adapter and is guarded across workers by a PostgreSQL advisory lock.
tags: [arxiv, adapters, core-mechanism]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-10-31T00:00:00Z }  # decided by human:jx-nin
---

# Decision

* Resolves the placement part of Q-14 in the [specification](/specs/tds.md) (v0.4, sections 5.2 and 6.6.1): `src/arx/adapters/arxiv/`, not `jobs/`.
* The limit is an arXiv policy (NFR-16), and every arXiv request, harvest or conversion fetch, goes through the arXiv client.
* An in-process token bucket alone cannot stop a second worker; the PostgreSQL advisory lock from 6.6.1 does, so the limiter needs a database connection or lock injected.
* Core mechanism: the owner implements it in M1; agents write its failing tests.
* M0's manual script waits a fixed interval between requests instead, marked as a `shortcut:` comment.
