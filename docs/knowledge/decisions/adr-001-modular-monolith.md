---
type: Decision
title: "ADR-001 Modular monolith"
description: One codebase and one database, run as an api process and a worker process.
tags: [architecture, adr]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-10-30T00:00:00Z }
---

# Decision

* One Python codebase and one PostgreSQL database, run as two processes: `api` (HTTP, UI) and `worker` (scheduler, jobs).
* Single user on a single node, so this costs the least to run.
* Layering will be enforced with import-linter, added with the first package that needs it: `domain` imports nothing else, services depend on adapter `Protocol`s, and concrete adapters are wired in `bootstrap.py`. A module can be pulled out later without a redesign.

Summary row: [specification](/specs/tds.md), section 13.
