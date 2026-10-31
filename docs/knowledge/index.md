---
okf_version: "0.2"
---

# Specifications

* [Technical Design Specification](/specs/tds.md) - authoritative requirements and design, source in `docs/spec/tds.md`

# Components

* [EPUB conversion](/components/epub-conversion.md) - arXiv HTML to EPUB 3 via pandoc with a Kindle stylesheet (M0)
* [Kindle delivery](/components/kindle-delivery.md) - EPUB by e-mail over Gmail SMTP, recipient allowlist and size limit (M0)

# Decisions

* [Tooling stack](/decisions/tooling.md) - ruff + mypy --strict + pytest-cov + sphinx, enforced by pre-commit and CI
* [Merge request review](/decisions/review.md) - mr-reviewer agent checks every MR in a fresh context
* [Test layout](/decisions/test-layout.md) - tests mirror src/arx/, levels via pytest markers
* [ADR-001 Modular monolith](/decisions/adr-001-modular-monolith.md) - one codebase, api + worker processes
* [ADR-002 PostgreSQL job queue](/decisions/adr-002-postgres-job-queue.md) - SKIP LOCKED queue instead of Redis/Celery
* [ADR-003 pgvector](/decisions/adr-003-pgvector.md) - vector search inside PostgreSQL
* [ADR-004 fastembed](/decisions/adr-004-fastembed.md) - CPU embeddings with bge-small-en-v1.5
* [ADR-005 LiteLLM](/decisions/adr-005-litellm.md) - provider-agnostic LLM gateway
* [ADR-006 Maths to PNG](/decisions/adr-006-math-png.md) - proposed, pending device test
* [ADR-007 HTMX UI](/decisions/adr-007-htmx.md) - server-rendered templates, no SPA
* [ADR-008 GitOps](/decisions/adr-008-gitops.md) - Argo CD pull deployment in phase 2
* [ADR-009 Isolated converter](/decisions/adr-009-converter-isolation.md) - sandboxed document tooling
* [ADR-010 Python 3.14](/decisions/adr-010-python.md) - newest version all dependencies support
* [Test-driven development](/decisions/tdd.md) - test-first in every layer, named exceptions, one commit per behaviour
* [Database driver psycopg 3](/decisions/db-driver.md) - one driver for async app code and sync Alembic/CLI
* [Default Kindle profile](/decisions/kindle-profile.md) - Paperwhite 11th gen Signature, 1236 × 1648 px, 300 dpi, greyscale
* [SMTP provider Gmail](/decisions/smtp-provider.md) - dedicated Gmail account, app password, 20 MiB attachment limit
* [Mail and settings libraries](/decisions/mail-library.md) - stdlib smtplib until the async worker, pydantic-settings for configuration
* [Logging with stdlib and structlog](/decisions/logging.md) - stdlib loggers in modules, structlog JSON formatter in the entry point
* [arXiv rate limiter placement](/decisions/arxiv-rate-limiter.md) - in adapters/arxiv/, advisory lock across workers
