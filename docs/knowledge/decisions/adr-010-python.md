---
type: Decision
title: "ADR-010 Python 3.14"
description: Python 3.14 is the implementation language and pinned version.
tags: [language, tooling, adr]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-10-30T00:00:00Z }
---

# Decision

* The workload is bound by I/O and rate limits, and Python has the strongest ML/LLM ecosystem.
* 3.14 is the newest version every planned dependency ships wheels for. The spec draft said 3.13 and the scaffold said 3.15, but onnxruntime has no 3.15 wheels.
* Upgrade only after checking that the native dependencies (onnxruntime, psycopg, lxml, pillow) ship wheels for the new version.

Summary row: [specification](/specs/tds.md), section 13.
