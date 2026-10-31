---
type: Decision
title: Logging with stdlib and structlog
description: Modules use stdlib loggers; structlog only formats JSON output in the entry point.
tags: [observability, logging]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-10-31T00:00:00Z }  # decided by human:jx-nin
---

# Decision

* Answers Q-13 of the [specification](/specs/tds.md) (v0.4, sections 5.5 and 8.1).
* Every module: `logger = logging.getLogger(__name__)`, as the project rules require; no module imports structlog.
* The entry point configures handlers and installs `structlog.stdlib.ProcessorFormatter` for JSON output and the redaction processor.
* structlog is added as a dependency by the slice that first needs JSON logs (M1); until then the entry point uses plain stdlib formatting.
* Trade-off: context fields such as `job_id` are passed through `extra=` or contextvars instead of structlog's bound loggers.
