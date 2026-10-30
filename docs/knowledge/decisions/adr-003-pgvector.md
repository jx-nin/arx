---
type: Decision
title: "ADR-003 pgvector for vector search"
description: Embeddings are stored and searched in PostgreSQL with pgvector HNSW.
tags: [architecture, search, adr]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-10-30T00:00:00Z }
---

# Decision

* The corpus stays at or below 10^5 vectors, and HNSW inside Postgres is enough at that size.
* No separate vector database to run.

Summary row: [specification](/specs/tds.md), section 13.
