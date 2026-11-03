# Log

## 2026-11-03

* Spec moves to v0.10. Added [keyword search of all of arXiv](/decisions/arxiv-search.md) (FR-DSC-08) and [digest of a queue](/decisions/digest-queue.md) (FR-DLV-08, FR-DLV-04, digests move from M8 to M1). Updated [arXiv rate limiter placement](/decisions/arxiv-rate-limiter.md): the lock also spaces CLI searches. Owner decisions: M1 search shows only *sent* and *stored*; queued papers without HTML are removed at the digest run and reported.
* Spec moves to v0.9. Added [arXiv client and send by ID or URL](/components/arxiv-client.md): reference parser, arXiv API and HTML client, `KindleService`, `arx kindle` CLI command. Updated [Kindle delivery](/components/kindle-delivery.md) with `check_recipient`.

## 2026-10-31

* Spec moves to v0.8. Updated [Kindle delivery](/components/kindle-delivery.md): wired in `bootstrap.py`, `arx send` CLI command.
* Spec moves to v0.7. Added [Kindle delivery](/components/kindle-delivery.md): delivery service, smtplib mailer and pydantic settings; added [mail and settings libraries](/decisions/mail-library.md).
* Spec moves to v0.6. Added [EPUB conversion](/components/epub-conversion.md): conversion service, LaTeXML HTML cleaner, pandoc EPUB builder and Kindle stylesheet.
* Spec moves to v0.5: agents implement core mechanisms too, review is agentic. Updated [test-driven development](/decisions/tdd.md), [merge request review](/decisions/review.md), [arXiv rate limiter placement](/decisions/arxiv-rate-limiter.md) and [ADR-002](/decisions/adr-002-postgres-job-queue.md).
* Spec moves to v0.4. Added [database driver psycopg 3](/decisions/db-driver.md), [default Kindle profile](/decisions/kindle-profile.md), [SMTP provider Gmail](/decisions/smtp-provider.md), [logging with stdlib and structlog](/decisions/logging.md) and [arXiv rate limiter placement](/decisions/arxiv-rate-limiter.md); updated the [specification](/specs/tds.md) and [ADR-010](/decisions/adr-010-python.md).

## 2026-10-30

* Added [test-driven development](/decisions/tdd.md); spec moves to v0.3.
* Added the [specification](/specs/tds.md) (v0.2), ADR-001..010 as decisions starting at [ADR-001](/decisions/adr-001-modular-monolith.md), and [test layout](/decisions/test-layout.md). Updated [tooling stack](/decisions/tooling.md) with Python 3.14 and CI.
* Added [merge request review](/decisions/review.md).
* Created the bundle. Added [tooling stack](/decisions/tooling.md).
