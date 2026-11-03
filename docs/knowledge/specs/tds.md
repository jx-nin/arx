---
type: Specification
title: Technical Design Specification
description: Authoritative requirements and design for Arx; requirement IDs (FR-*, NFR-*, ADR-*) are referenced from commits, tests and MRs.
tags: [spec, requirements]
status: draft
generated: { by: "agent:claude-opus-5-5", at: 2026-10-31T00:00:00Z }
---

# Specification

* Source: `docs/spec/tds.md`. It is a living document: change it in the same MR as the behaviour it describes, and add a row to its revision history.
* Architecture decisions live in this bundle as `Decision` concepts (`/decisions/adr-NNN-*.md`). The spec's section 13 is only a summary.
* Open questions Q-1..Q-14 (section 15.2) must be answered before their milestone starts. v0.4 answers Q-1, Q-4, Q-11, Q-13 and Q-14; the answers are the decisions [default Kindle profile](/decisions/kindle-profile.md), [SMTP provider Gmail](/decisions/smtp-provider.md), [database driver psycopg 3](/decisions/db-driver.md), [logging with stdlib and structlog](/decisions/logging.md) and [arXiv rate limiter placement](/decisions/arxiv-rate-limiter.md). v0.10 answers Q-3 ([maths as MathML](/decisions/maths-mathml.md), rejecting [ADR-006](/decisions/adr-006-math-png.md)), Q-7 ([web UI access before owner login](/decisions/ui-access.md)) and Q-8: the converter serves an internal HTTP API to the worker ([ADR-009](/decisions/adr-009-converter-isolation.md)).
