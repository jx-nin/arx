---
type: Component
title: arXiv client and send by ID or URL
description: M0 path that looks up a paper in the arXiv API, downloads its HTML rendition, converts it and mails it to the Kindle (`arx kindle`).
tags: [arxiv, ingestion, delivery, kindle]
status: draft
generated: { by: "agent:claude-opus-5-5", at: 2026-11-03T00:00:00Z }
---

# Component

* Covers FR-ING-04 (ID and URL, HTML path only) and FR-DLV-01 for M0 (spec 6.6.1); storing the paper (M1), the library (M3) and the PDF fallback (FR-CNV-05) follow later.
* `domain/arxiv_id.py`: `parse_reference` reads new- and old-style IDs, `arXiv:` prefixes and `arxiv.org/abs|pdf|html/` URLs into a `PaperRef` (version `None` = latest); `VERSIONED_ID` is shared with `arx send`.
* `adapters/arxiv/client.py`: `ArxivClient.paper` queries the API with `id_list` and parses the Atom entry with lxml (no entity expansion, no network); `html` downloads `arxiv.org/html/<id>v<n>`. Redirects are followed; 404 returns `None`, other HTTP and network errors raise `OSError` with a one-line reason; a non-XML body or an entry whose ID is not an `arxiv.org/abs/<id>v<n>` URL (an API error report) raises `ValueError`. Endpoints are fixed until the `ARX_ARXIV_*_BASE` settings (M1).
* Requests are spaced by `ARX_ARXIV_MIN_INTERVAL_S` (M0 exception); the [rate limiter](/decisions/arxiv-rate-limiter.md) replaces the wait in M1. The client is synchronous until the async worker.
* The API carries no licence, so `Paper.license` is `None` and the title page omits it.
* `services/kindle.py`: `KindleService.send` checks the recipient first, then fetches, converts via [EPUB conversion](/components/epub-conversion.md) and mails via [Kindle delivery](/components/kindle-delivery.md); `PaperNotFoundError` and `HtmlUnavailableError` are `ValueError`s.
* `bootstrap.py`: `build_arxiv_client` sets `User-Agent` from `ARX_ARXIV_USER_AGENT`, defaulting to `arx/<ver> (mailto:<ARX_DELIVERY_FROM>)`; `build_kindle_service` wires the three adapters.
* `cli/main.py`: `arx kindle REF --to ADDR`; rejections and request errors exit with a one-line reason.
