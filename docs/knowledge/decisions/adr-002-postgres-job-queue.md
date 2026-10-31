---
type: Decision
title: "ADR-002 PostgreSQL job queue"
description: Jobs run from a PostgreSQL table using FOR UPDATE SKIP LOCKED instead of Redis/Celery.
tags: [architecture, jobs, adr]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-10-30T00:00:00Z }
---

# Decision

* Queue, leases, retries, dependencies and schedules live in PostgreSQL (spec 6.3).
* No extra service on an 8 GB host, enqueue happens in the same transaction as the business change, and every job is visible through SQL.
* Trade-off: retries, leases and scheduling are built in-house. This is a deliberate learning goal.

Summary row: [specification](/specs/tds.md), section 13.
