---
title: "Arx — arXiv Discovery & Kindle Delivery Service"
subtitle: "Technical Design Specification"
date: "3 November 2026"
version: "0.13 (Draft)"
---

# Document Control

| Field | Value |
|---|---|
| Document | Technical Design Specification (TDS) |
| System | Arx |
| Version | 0.13 — Draft |
| Status | Proposed, ready for implementation of Milestone M0–M1 |
| Date | 3 November 2026 |
| Audience | Implementer(s), reviewers, AI coding agents executing scoped changes |

## Revision History

| Version | Date | Change |
|---|---|---|
| 0.13 | 2026-11-03 | Answered Q-3: MathML renders on the Paperwhite 11 Signature, so ADR-006 (maths as PNG) is rejected; FR-CNV-02, 5.2, 5.5, 6.1, 6.5.1 steps 2, 4 and 9, 6.5.4, 13, 14 (M0, M1), R-2: maths as MathML via pandoc `--mathml`, no MathJax/resvg. Answered Q-7: tailnet-only access without login until M3, which adds owner login FR-ADM-05 (3.10, 7.2 T1, 14). Answered Q-8: the converter is a long-running service with an internal HTTP API that the worker calls, the same in Compose and k3s (5.2, 6.1, 6.5.4, 7.2 T3, 11.1, 11.2, ADR-009). Appendix A: FR-CNV-02, FR-ADM-05 |
| 0.12 | 2026-11-03 | New FR-DSC-08 (P0): keyword search of all of arXiv via the API `search_query`, each result marked as stored, in the library or sent; FR-ING-08 (saved searches, P2) builds on it. Sections 3.1, 6.6.1 (search endpoint row, `arx search`, advisory lock held for the interval so CLI and workers stay spaced), 6.7 (`GET /api/v1/search`), 6.8 (Search view), 14 (CLI in M1, Search view in M3), Appendix A. Digest of a queue: new FR-DLV-08 (P0) digest queue; FR-DLV-04 sends the queued papers daily or weekly, no longer the top-ranked ones, split above the attachment limit; FR-DLV-04 and FR-CNV-07 raised to P0; NFR-08 counts runs with at least one sendable queued paper. Sections 1.6, 3.1, 5.3, 6.2 (`digest_queue_item` with the claiming delivery, `digest_part`; retention keeps queued and sent papers), 6.3.4 (`digest` job), 6.5.3 (claim, split, release), 6.7 (queue endpoints; ad-hoc digest cites FR-DLV-01, FR-CNV-07), 6.8, 12 (`ARX_DIGEST_CRON`, `ARX_DIGEST_RECIPIENT`), 14 (digests move from M8 to M1), Appendix A. `build_digest` is keyed by its delivery (6.3.4); a failure hook on `dead`/`cancelled` fails the delivery and releases its items (6.3.3); `fetch_paper` can queue after import (own key `fetch_queue:<id>`); `delivery_item` cascades with its conversion, and cache eviction keeps conversion rows (6.2.3, FR-DAT-03); only single-paper deliveries are retried (6.5.3, 6.8). Owner decisions: M1 search shows only *sent* and *stored*, *library* arrives in M3 (FR-DSC-08, 6.6.1, 14, Appendix A incl. FR-ING-04 "stored" in M1); queued papers without an HTML rendition are removed at the digest run and reported (FR-DLV-08, 6.5.3), with the report shown in 6.7 and 6.8. Job retry is refused (409) for digest jobs (6.5.3, 6.7, 6.8); an evicted file is a cache miss regenerated into the same conversion row |
| 0.11 | 2026-11-03 | Section 6.2.2: M0 migration creates only `paper`, `primary_category` nullable until the harvest, pgvector extension with the first embedding table; papers stored once per arXiv ID at the latest version, synchronous until the worker (5.5). Section 12: `ARX_DATABASE_URL_FILE` replaces `ARX_DATABASE_URL`. Appendix A: FR-ING-03 (M0 partial), FR-ING-07; section 12: unprefixed `.env` keys ignored, unknown `ARX_*` keys rejected |
| 0.10 | 2026-11-03 | Section 6.6.1: M0 command `arx today CATEGORY` lists the latest announced new papers and cross-lists of one category from `rss.arxiv.org`, replacements left out; RSS is the M0 stopgap for Q-2, which stays open for the M1 spike. Section 5.5: M0 parses Atom and RSS with lxml. Section 14: M0 lists one category's papers with `arx today`. Appendix A: FR-ING-02 partial in M0 |
| 0.9 | 2026-11-03 | Section 6.6.1: M0 command `arx kindle` fetches a paper by ID or URL, converts and mails it; metadata from the API, licence not available there; `ARX_ARXIV_USER_AGENT` defaults to Arx with the sender as contact (12). Section 14: M0 sends a paper by ID or URL before the category harvest. Appendix A: FR-ING-04, FR-DLV-01; FR-DLV-07 and NFR-16 test paths |
| 0.8 | 2026-10-31 | Section 6.6.3: M0 command `arx send` mails an EPUB with paper metadata from flags; Appendix A: FR-DLV-02, FR-DLV-03 and FR-DLV-07 test paths |
| 0.7 | 2026-10-31 | Sections 5.5 and 6.6.3: mail via stdlib `smtplib` until the async worker; attachment filename rule; recipients checked case-insensitively and must be `@kindle.com`; oversized files rejected, downscale option in M1; `ARX_DELIVERY_ALLOWED_RECIPIENTS` named with its prefix. Section 12: SMTP host and port default to Gmail. Appendix A: FR-DLV-02, FR-DLV-03, FR-DLV-07 |
| 0.6 | 2026-10-31 | Section 6.5.1 steps 3 and 9: drop LaTeXML front matter repeated on the title page; pandoc builds without its own title page, language `en`; M0 implements step 3 without heading normalisation; Appendix A: FR-CNV-01 test paths and milestones |
| 0.5 | 2026-10-31 | Sections 9.1 and 14: agents implement core mechanisms too; review is agentic (`mr-reviewer`), with questions and adjustments from the owner |
| 0.4 | 2026-10-31 | Answered Q-1 (default profile Paperwhite 11 Signature, 6.5), Q-4 (dedicated Gmail account, 6.6.3; attachment limit default 20 MiB), Q-11 (psycopg 3, 5.5), Q-13 (stdlib loggers with structlog formatter, 5.5, 8.1) and Q-14 (fixes in 5.2, 6.3.4, FR-CNV-09, FR-DSC-03); added an Answer column to 15.2 |
| 0.3 | 2026-10-30 | Section 9.1: test-driven development in every layer with named exceptions; core mechanisms get agent-written tests and owner-written code; TDD steps are not committed separately |
| 0.2 | 2026-10-30 | Aligned with repository decisions: Python 3.14, mypy instead of pyright, 90% coverage, tests mirror `src/arx/` with level markers, ADRs kept in the OKF knowledge bundle; added open questions Q-7..Q-14 |
| 0.1 | 2026-10-30 | Initial draft: requirements, architecture, data model, pipelines, security, operations, roadmap |

## Conventions

- The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT** and **MAY** are to be interpreted as described in RFC 2119.
- Functional requirements are identified as `FR-<AREA>-<NN>`, non-functional requirements as `NFR-<NN>`, architecture decisions as `ADR-<NNN>`. Identifiers are stable and are intended to be referenced from commits, pull requests, tests and spec changes.
- Priorities: **P0** (MVP, required for the first usable release), **P1** (required for v1.0), **P2** (post-v1.0 / stretch).
- External facts that are subject to change (rate limits, size limits, URLs) are marked *(verify)* and MUST be configurable rather than hard-coded.


# 1. Introduction

## 1.1 Purpose

This document specifies the design of **Arx**, a self-hosted, single-user service that:

1. **discovers** newly published arXiv papers that match the owner's interests,
2. **manages** a personal paper library (statuses, tags, notes, semantic search), and
3. **delivers** papers to an Amazon Kindle in a reflowable, e-ink-optimised EPUB format instead of fixed-layout, multi-column PDFs.

It is the authoritative reference for implementation, testing, deployment and operation of the system.

## 1.2 Problem Statement

Research papers on arXiv are distributed primarily as PDFs typeset for A4/Letter paper, frequently in two columns. On a 6–7" e-ink display these documents require constant zooming and panning, which makes reading tiring. In addition, the volume of daily submissions makes it impractical to find relevant papers manually across several categories.

Since December 2023 arXiv generates an HTML rendition (via LaTeXML) for new submissions made in TeX/LaTeX when the conversion succeeds, and is backfilling older papers. This HTML is a structurally rich source from which a clean, reflowable EPUB can be produced.

## 1.3 Goals

| ID | Goal |
|---|---|
| G-1 | Surface a short, ranked daily list of new papers that are relevant to the owner, with a plain-language explanation of each. |
| G-2 | Produce EPUB files that are comfortable to read on a Kindle: reflowable text, readable figures and tables, legible mathematics. |
| G-3 | Deliver papers to the Kindle with one action, individually or as a digest bundle. |
| G-4 | Maintain a searchable personal library, including semantic ("find what I read about X") search. |
| G-5 | Run reliably on constrained home hardware (Lenovo M710q, 8 GB RAM) and be accessible from a phone over a private network. |
| G-6 | Serve as a production-grade engineering showcase: secure SDLC, CI/CD, IaC, GitOps, observability and LLM evaluation. |

## 1.4 Non-Goals

- Multi-user or multi-tenant operation; public sign-up; public internet exposure.
- Circumventing paywalls or accessing content outside arXiv's published terms of use.
- Native mobile applications (a responsive web UI is sufficient).
- Real-time synchronisation of reading position with the Kindle (not exposed by Amazon).
- A general-purpose PDF repair tool for arbitrary scanned documents (only a fallback for arXiv PDFs is in scope).

## 1.5 Scope Summary

In scope: ingestion of arXiv metadata, ranking, enrichment (embeddings, LLM summaries), library management, conversion (HTML→EPUB, PDF fallback), delivery (Send to Kindle via e-mail), web UI, REST API, background job processing, observability, security controls, CI/CD, containerised deployment (Docker Compose, then Kubernetes/k3s), cloud backups (AWS or Azure via Terraform).

## 1.6 Glossary

| Term | Definition |
|---|---|
| arXiv ID | Canonical identifier of a paper, e.g. `2410.12345`; versions are suffixed `v1`, `v2`, … |
| Abstract page | `arxiv.org/abs/<id>` — metadata landing page |
| HTML rendition | LaTeXML-generated HTML of a paper, served under `arxiv.org/html/<id>` *(verify)* |
| Digest | A bundle of several papers converted into one EPUB with a table of contents |
| Digest queue | Papers the owner picked for the next scheduled digest |
| Interest profile | Vector representation of the owner's interests, derived from seed topics and feedback |
| Job | A unit of asynchronous work persisted in the database queue |
| Send to Kindle | Amazon service that accepts documents by e-mail to a personal `@kindle.com` address from an approved sender |
| Kindle profile | Device-specific rendering parameters (screen width, image DPI, greyscale) |
| Owner | The single authorised user of the system |


# 2. Overall Description

## 2.1 Product Perspective

Arx is a standalone service hosted on the owner's homelab. It integrates with four external systems:

```
                 +-------------------+
                 |   Owner (phone /  |
                 |   laptop browser) |
                 +---------+---------+
                           | HTTPS over Tailscale (tailnet only)
                           v
+-----------+     +--------+---------+     +-------------------+
|  arXiv    |<----|       Arx        |---->|  LLM provider     |
| API / RSS |     |  (api + worker)  |     |  (via LiteLLM)    |
| HTML/PDF  |     +--------+---------+     +-------------------+
+-----------+              |
                           | SMTP (TLS)
                           v
                 +-------------------+          +-----------------+
                 | Mail relay / SMTP |--------->| Send to Kindle  |
                 +-------------------+          | -> Kindle device|
                                                +-----------------+
                           |
                           v  (encrypted backups)
                 +-------------------+
                 | Object storage    |
                 | (S3 / Azure Blob) |
                 +-------------------+
```

## 2.2 User Profile

A single technically proficient owner who reads on a Kindle, browses on a phone, and administers the homelab. Usage pattern: a short morning review of the daily ranked list on the phone, queueing papers, and reading on the Kindle later.

## 2.3 Operating Environment

| Aspect | Constraint |
|---|---|
| Host | Lenovo ThinkCentre M710q, Intel Core i5 (7th gen), 8 GB RAM, 256 GB SSD |
| OS | Debian 13 |
| Runtime | Docker Engine; later k3s (single node) |
| Existing homelab tooling | Dockhand (container management), Uptime Kuma (uptime monitoring), Tailscale (remote access) |
| Optional compute | Laptop with RTX 3060 (mobile) for local LLM inference via Ollama when online |
| Cloud | AWS (credits available) or Azure — backups, optional off-site environment |

## 2.4 Design and Implementation Constraints

- **C-1** The entire production stack MUST fit within 8 GB RAM, leaving at least 1.5 GB headroom for the OS and other homelab services.
- **C-2** All requests to arXiv legacy APIs (API, RSS, OAI-PMH) MUST be serialised over a single connection with at most one request every three seconds *(verify; configurable)*.
- **C-3** Paper content MAY be retrieved, stored and used for personal use only, consistent with arXiv's API terms. Metadata is CC0.
- **C-4** No GPU is available on the host; all always-on ML inference MUST run on CPU.
- **C-5** The service MUST NOT be reachable from the public internet.

## 2.5 Assumptions and Dependencies

- A-1: arXiv's HTML rendition remains available for the majority of new submissions.
- A-2: Send to Kindle continues to accept EPUB attachments by e-mail from approved senders *(verify current formats and size limits)*.
- A-3: An SMTP account with app-password or token authentication is available.
- A-4: An LLM API key is available; monthly spend is capped (see NFR-14).


# 3. Functional Requirements

## 3.1 Feature Overview

| Area | Code | Features |
|---|---|---|
| Ingestion | ING | Category subscriptions, daily harvest, on-demand import by ID/URL, deduplication, version tracking |
| Enrichment | ENR | Embeddings, LLM "plain-language" summaries, keyword extraction, HTML availability detection |
| Discovery | DSC | Interest profile, ranking, daily feed, feedback loop, explanations, filters, keyword search of arXiv |
| Library | LIB | Statuses, tags, notes, collections, full-text and semantic search, export |
| Conversion | CNV | HTML→EPUB, math rendering, figure/table handling, PDF fallback, Kindle profiles, digests |
| Delivery | DLV | Send to Kindle, digest queue with scheduled digests, delivery history, retries |
| Assistant | AST | Question answering over the library (RAG), reading-list suggestions |
| Web UI | UI | Responsive phone-first interface |
| Administration | ADM | Settings, job monitor, budget, health |
| Data | DAT | Backup, restore, export |

## 3.2 Ingestion (ING)

| ID | Requirement | Priority |
|---|---|---|
| FR-ING-01 | The owner MUST be able to subscribe to one or more arXiv categories (e.g. `cs.LG`, `astro-ph.HE`, `q-bio.NC`) and to unsubscribe from them. | P0 |
| FR-ING-02 | The system MUST harvest metadata of new submissions for all subscribed categories once per day at a configurable time, after arXiv's daily announcement. | P0 |
| FR-ING-03 | Harvesting MUST be idempotent: re-running a harvest for the same date MUST NOT create duplicate papers. | P0 |
| FR-ING-04 | The owner MUST be able to import a single paper by arXiv ID, abstract URL, PDF URL or HTML URL. | P0 |
| FR-ING-05 | The system MUST store, per paper: arXiv ID, latest version, title, authors, abstract, primary and cross-list categories, submission and update dates, DOI and journal reference when present, licence, and links. | P0 |
| FR-ING-06 | The system SHOULD detect new versions of papers in the library and flag them. | P1 |
| FR-ING-07 | Cross-listed papers appearing in several subscribed categories MUST be stored once. | P0 |
| FR-ING-08 | The system MAY support saved searches: a stored FR-DSC-08 query that runs with the daily harvest and feeds its new matches into ranking, in addition to categories. | P2 |

## 3.3 Enrichment (ENR)

| ID | Requirement | Priority |
|---|---|---|
| FR-ENR-01 | For each ingested paper the system MUST compute a dense embedding of `title + abstract` using a locally executed model. | P0 |
| FR-ENR-02 | The system MUST determine whether an HTML rendition is available and record the result (`available`, `unavailable`, `unknown`). | P0 |
| FR-ENR-03 | For papers above a configurable relevance threshold, the system SHOULD generate a plain-language summary (2–4 sentences, non-specialist audience) and a one-line "why this may interest you" explanation via an LLM. | P1 |
| FR-ENR-04 | LLM outputs MUST be stored together with the model identifier, prompt version, token usage and cost. | P1 |
| FR-ENR-05 | The system MAY extract 3–7 keywords per paper for faceted browsing. | P2 |

## 3.4 Discovery (DSC)

| ID | Requirement | Priority |
|---|---|---|
| FR-DSC-01 | The owner MUST be able to define seed interests as free-text statements (e.g. "fusion reactor plasma control", "graph neural networks for chemistry"). | P0 |
| FR-DSC-02 | The system MUST rank each day's new papers by relevance using the algorithm in Section 6.4 and present the top *N* (default 20) as the daily feed. | P0 |
| FR-DSC-03 | The owner MUST be able to give feedback per paper: *interesting*, *not interesting*, *save*, *send to Kindle* (stored as signals `interesting`, `not_interesting`, `saved`, `sent`). Feedback MUST influence subsequent rankings. | P0 |
| FR-DSC-04 | Each feed entry SHOULD show which seed interest or past paper contributed most to its score. | P1 |
| FR-DSC-05 | The feed MUST support filtering by category, date range, HTML availability and minimum score. | P1 |
| FR-DSC-06 | The system SHOULD reserve a configurable share of the feed (default 10%) for "exploration" items outside the owner's usual topics to avoid filter bubbles. | P1 |
| FR-DSC-07 | The owner MUST be able to find similar papers to any given paper ("more like this"). | P1 |
| FR-DSC-08 | The owner MUST be able to search all of arXiv by keyword (arXiv API `search_query`, 6.6.1), not only stored papers (FR-LIB-04). Each result MUST show whether the paper already exists in Arx: *sent* (date of the last sent delivery that carried it, alone or in a digest) and *library* (with its status), both when both apply, otherwise *stored* (harvested or imported only); a result without a marker is new to Arx. In M1 only *sent* and *stored* exist; *library* arrives in M3 with library statuses (FR-LIB-01). From each result the owner MUST be able to send or queue the paper, either of which imports it (FR-ING-04, FR-DLV-01, FR-DLV-08). | P0 |

## 3.5 Library (LIB)

| ID | Requirement | Priority |
|---|---|---|
| FR-LIB-01 | Papers saved by the owner MUST enter the library with status `to_read`. Statuses: `to_read`, `reading`, `read`, `archived`. | P0 |
| FR-LIB-02 | The owner MUST be able to add, remove and rename tags and assign multiple tags per paper. | P0 |
| FR-LIB-03 | The owner MUST be able to attach Markdown notes to a paper. | P1 |
| FR-LIB-04 | The library MUST support keyword search (PostgreSQL full-text search over title, abstract, notes) and semantic search (vector similarity over embeddings). | P0 (keyword), P1 (semantic) |
| FR-LIB-05 | The owner SHOULD be able to group papers into named collections (e.g. "Weekend reading"). | P1 |
| FR-LIB-06 | The system MUST export the library as BibTeX and as JSON. | P1 |
| FR-LIB-07 | The system MAY import highlights and notes from the Kindle (`My Clippings.txt` upload) and attach them to the matching paper. | P2 |

## 3.6 Conversion (CNV)

| ID | Requirement | Priority |
|---|---|---|
| FR-CNV-01 | When an HTML rendition is available, the system MUST convert it to a valid EPUB 3 file containing: title page (title, authors, arXiv ID, date, licence, link), navigable table of contents, body text, figures, tables, references. | P0 |
| FR-CNV-02 | Mathematics MUST be legible on the target device. Display and inline maths SHOULD be embedded as MathML with the TeX source preserved as an `application/x-tex` annotation (Q-3; ADR-006 rejected). | P0 |
| FR-CNV-03 | Figures MUST be fetched, converted to greyscale, resized to the target profile width and embedded. | P0 |
| FR-CNV-04 | Tables wider than the target width SHOULD be rendered as images; narrow tables SHOULD remain as HTML tables. | P1 |
| FR-CNV-05 | When no HTML rendition is available, the system MUST fall back to reflowing the PDF for the target screen (k2pdfopt) and produce a PDF optimised for the device. | P1 |
| FR-CNV-06 | The owner MUST be able to configure Kindle profiles (name, screen resolution, image DPI, font scale) and select a default. | P1 |
| FR-CNV-07 | The system MUST be able to produce a digest EPUB bundling several papers with a combined table of contents. | P0 |
| FR-CNV-08 | Every produced EPUB MUST pass `epubcheck` validation; failures MUST be recorded with diagnostics. | P0 |
| FR-CNV-09 | Conversion outputs MUST be cached by `(arxiv_id, version, profile_id, kind, converter_version)` and reused. | P0 |
| FR-CNV-10 | The owner SHOULD be able to download any converted file from the web UI. | P0 |

## 3.7 Delivery (DLV)

| ID | Requirement | Priority |
|---|---|---|
| FR-DLV-01 | The owner MUST be able to send a single paper to the Kindle with one action. | P0 |
| FR-DLV-02 | Delivery MUST use e-mail to the configured `@kindle.com` address from an approved sender, with the converted file as attachment. | P0 |
| FR-DLV-03 | Files exceeding the configured attachment size limit *(verify; default 20 MiB of raw file, leaving headroom under the sending provider's 25 MB limit, see 6.6.3)* MUST be rejected before sending, with a clear message and a downscale option. | P0 |
| FR-DLV-04 | The owner MUST be able to schedule the digest daily or weekly (`ARX_DIGEST_CRON`, 12). Each run sends the papers in the digest queue (FR-DLV-08) as one digest EPUB (FR-CNV-07), split into several when they exceed the attachment limit (6.5.3); an empty queue sends nothing. Papers are never added to the digest automatically. | P0 |
| FR-DLV-05 | The system MUST keep a delivery history (paper(s), file hash, size, timestamp, outcome, error). | P0 |
| FR-DLV-06 | Transient delivery failures MUST be retried with exponential backoff; permanent failures MUST be surfaced in the UI. | P0 |
| FR-DLV-07 | Recipient addresses MUST be restricted to an allowlist stored in configuration. | P0 |
| FR-DLV-08 | The owner MUST be able to add papers to the digest queue (by ID or URL, or from search results, the feed or the library), list it and remove papers from it. A paper is queued at most once. A sent digest removes its papers from the queue; after a permanent failure they stay queued. Two exceptions are removed at the digest run with a named reason: a paper too large to send on its own (FR-DLV-03), and a paper without an HTML rendition (`html_status` `unavailable`) until the PDF path exists. | P0 |

## 3.8 Assistant (AST)

| ID | Requirement | Priority |
|---|---|---|
| FR-AST-01 | The owner SHOULD be able to ask natural-language questions over papers in the library ("what did I read about tokamak disruptions?"); answers MUST cite the papers (and sections) they are based on. | P2 |
| FR-AST-02 | Full text of library papers MAY be chunked and embedded to support FR-AST-01. | P2 |
| FR-AST-03 | The assistant MAY be implemented as an agent (e.g. LangGraph) with tools: library search, paper section retrieval, arXiv search. | P2 |

## 3.9 Web UI (UI)

| ID | Requirement | Priority |
|---|---|---|
| FR-UI-01 | The UI MUST be usable on a phone (≥ 360 px width) and desktop. | P0 |
| FR-UI-02 | Views: Today (feed), Paper detail, Library, Search, Deliveries, Settings, Jobs. | P0 |
| FR-UI-03 | Feedback and "send to Kindle" actions MUST be performable from the feed without a full page reload. | P0 |
| FR-UI-04 | The UI SHOULD support a dark theme. | P2 |

## 3.10 Administration (ADM)

| ID | Requirement | Priority |
|---|---|---|
| FR-ADM-01 | The owner MUST be able to manage settings: subscriptions, seed interests, schedules, Kindle profiles, delivery address, LLM provider and budget. | P0 |
| FR-ADM-02 | The UI MUST show the job queue: pending, running, failed jobs with error details, and allow retrying or cancelling a job. | P1 |
| FR-ADM-03 | The UI SHOULD show the current month's LLM spend versus budget. | P1 |
| FR-ADM-04 | The service MUST expose `/healthz` (liveness) and `/readyz` (readiness, incl. database connectivity). | P0 |
| FR-ADM-05 | The web UI and REST API MUST require an owner login: password checked against an Argon2id hash, session cookie (`Secure`, `HttpOnly`, `SameSite=Strict`), CSRF token on state-changing requests (7.2 T1). `/healthz`, `/readyz` and `/metrics` stay open; the M3 slice adds the login and logout routes to 6.7. Until then (M3), access is limited to the tailnet without login (Q-7). | P0 |

## 3.11 Data Management (DAT)

| ID | Requirement | Priority |
|---|---|---|
| FR-DAT-01 | The database MUST be backed up daily, encrypted client-side, and uploaded to off-site object storage. | P1 |
| FR-DAT-02 | A documented and tested restore procedure MUST exist; a restore test SHOULD be automated monthly. | P1 |
| FR-DAT-03 | Converted files are reproducible and therefore SHOULD NOT be backed up; their cache MAY be evicted (LRU) under disk pressure. Eviction removes files only, never conversion or delivery rows (6.2.3). | P1 |


# 4. Non-Functional Requirements

| ID | Category | Requirement | Target / Measure |
|---|---|---|---|
| NFR-01 | Performance | Feed page server response time | p95 < 300 ms for 50 items |
| NFR-02 | Performance | Single-paper conversion (HTML → EPUB, typical 10–30 pages) | p95 < 60 s on host |
| NFR-03 | Performance | Semantic search latency over ≤ 50 000 papers | p95 < 200 ms |
| NFR-04 | Throughput | Daily harvest of ≤ 5 subscribed categories completes | < 30 min end-to-end, including enrichment |
| NFR-05 | Resource | Steady-state memory of all Arx containers (api, worker, database) | < 2.5 GB total; worker peak < 1.5 GB |
| NFR-06 | Availability | Web UI availability (measured by Uptime Kuma / Prometheus probe) | ≥ 99% monthly (homelab-grade) |
| NFR-07 | Reliability | Jobs survive process and host restarts without loss | 0 lost jobs; at-least-once execution with idempotent handlers |
| NFR-08 | Reliability | Scheduled digest delivered | ≥ 95% of scheduled runs with at least one sendable queued paper (unclaimed, and `html_status` not `unavailable` at fire time, 6.5.3) |
| NFR-09 | Security | No service port exposed outside the tailnet / host | Verified by port scan in CI-deployed environment |
| NFR-10 | Security | Zero known critical vulnerabilities in released images | Gate in CI (Trivy) |
| NFR-11 | Maintainability | Test line coverage of `src/arx/` | ≥ 90%, enforced by `fail_under` in `pyproject.toml` |
| NFR-12 | Maintainability | Static typing | `mypy --strict` clean on `src/` and `tests/` |
| NFR-13 | Portability | All runtime configuration via environment variables / mounted secrets | 12-factor compliant |
| NFR-14 | Cost | LLM spend | Hard cap, default USD 5 / month; enrichment degrades gracefully to "no summary" |
| NFR-15 | Recoverability | RPO / RTO for the database | RPO ≤ 24 h, RTO ≤ 1 h |
| NFR-16 | Compliance | arXiv rate limits respected | 0 requests closer than the configured interval (enforced and metered) |
| NFR-17 | Observability | Every job and request is traceable by correlation ID across logs | 100% of log lines carry `request_id` or `job_id` |
| NFR-18 | Accessibility (output) | EPUB validity | 100% of delivered EPUBs pass `epubcheck` |


# 5. System Architecture

## 5.1 Architectural Style

Arx is a **modular monolith**: a single Python codebase, a single PostgreSQL database, executed as two process types:

| Process | Responsibility | Scaling |
|---|---|---|
| `api` | HTTP server: web UI (server-rendered), REST API, health and metrics endpoints | 1 replica (stateless; can scale horizontally) |
| `worker` | Scheduler and job executor: harvesting, enrichment, conversion, delivery, backups | 1 replica by design (single arXiv connection, see C-2); job concurrency per queue configurable |

Rationale is recorded in ADR-001. Module boundaries are enforced in code (import rules checked in CI with `import-linter`) so that modules could be extracted later without redesign.

## 5.2 Component View

```
+---------------------------------- arx (one codebase) ---------------------------------+
|                                                                                       |
|  web/ (Jinja + HTMX)     api/ (FastAPI routers)        cli/ (admin commands)          |
|          \                    |                          /                            |
|           +-------------- application services -------------------+                  |
|           |  discovery   library   conversion   delivery   admin  |                  |
|           +------+-----------+-----------+-----------+-------------+                  |
|                  |           |           |           |                                |
|  domain/ (entities, value objects, ranking, policies — no I/O)                        |
|                  |           |           |           |                                |
|  adapters/: arxiv_client  embedder  llm_gateway  epub_builder  mailer  storage  repo  |
|             (arxiv_client includes the rate_limiter, 6.6.1)                           |
|                                                                                       |
|  jobs/: queue (Postgres), scheduler, handlers                                         |
+---------------------------------------------------------------------------------------+
         |                |                 |                |               |
     PostgreSQL       arXiv APIs       LLM (LiteLLM)      pandoc /        SMTP relay
     + pgvector                                          k2pdfopt /
                                                         epubcheck
                                                         (converter, HTTP)
```

Layering rules:

- `domain` MUST NOT import from any other package.
- Application services depend on `domain` and on adapter **interfaces** (Python `Protocol`s), never on concrete adapters.
- Concrete adapters are wired in a composition root (`arx/bootstrap.py`).
- `web` and `api` depend only on application services.

## 5.3 Runtime View — Daily Pipeline

```
 06:30  scheduler enqueues  harvest(category, date)  for each subscription
           |
           v
 harvest  -> fetch listing (rate-limited) -> upsert papers -> enqueue embed(paper)
           |
           v
 embed    -> compute vector -> store -> (batch complete) enqueue rank(date)
           |
           v
 rank     -> score all new papers vs. interest profile -> persist feed(date)
           |       -> for top K enqueue summarize(paper) and probe_html(paper)
           v
 summarize-> LLM (budget-checked) -> store summary + explanation
 probe    -> HEAD/GET html rendition (rate-limited) -> store availability
           |
           v
 07:30  scheduler enqueues  digest  (daily or weekly)  -> claim queue -> build_digest -> deliver(digest)
```

## 5.4 Runtime View — "Send to Kindle"

1. Owner taps **Send** on a feed item (HTMX `POST /papers/{id}/deliveries`).
2. API validates request, creates `delivery` row (`status=queued`) and enqueues `convert(paper, profile)` followed by dependent `deliver(delivery_id)`.
3. Worker checks the conversion cache; on miss, runs the conversion pipeline (Section 6.5).
4. Worker sends the e-mail; updates `delivery.status` to `sent` or `failed`.
5. UI polls the delivery row (HTMX `hx-trigger="every 3s"` until terminal state) and shows the result.

## 5.5 Technology Stack

| Concern | Choice | Rationale |
|---|---|---|
| Language | Python 3.14 | Strongest ecosystem for embeddings/LLM/text processing; owner's primary language; I/O-bound workload where language speed is not the bottleneck. 3.14 is the newest version with wheels for every planned dependency (onnxruntime has none for 3.15 yet). |
| Packaging & tooling | uv, ruff (lint + format), mypy (strict), pre-commit | Fast, reproducible, modern; one type checker only |
| Web framework | FastAPI + Uvicorn | Async I/O, typed contracts, OpenAPI out of the box |
| UI | Jinja2 templates + HTMX, minimal CSS (Pico.css or hand-written) | No separate SPA build; ideal for a single-user phone-first UI |
| Database | PostgreSQL 17 + pgvector | One store for relational data, job queue, full-text and vector search |
| DB access | SQLAlchemy 2.x (async, Core + ORM) + psycopg 3 (Q-11) | Mature, typed, explicit SQL when needed; one driver serves async app code and sync Alembic/CLI. Repositories are synchronous like the M0 services until the async worker (M1) |
| Migrations | Alembic | Standard |
| Job queue | Custom PostgreSQL queue (`FOR UPDATE SKIP LOCKED`) | No additional infrastructure; transactional enqueue; learning value (ADR-002) |
| HTTP client | httpx (async) + tenacity | Timeouts, retries, HTTP/2 off for arXiv (single connection) |
| Feed parsing | feedparser (Atom), lxml | arXiv API returns Atom; M0 parses API Atom and category RSS with lxml, since feedparser ships no type hints |
| HTML processing | lxml / selectolax; nh3 for sanitisation | Fast, safe |
| Embeddings | fastembed (ONNX Runtime, CPU) with `BAAI/bge-small-en-v1.5` (384-d) | Small footprint, good quality, no PyTorch dependency (ADR-004) |
| LLM access | LiteLLM (library mode) | Provider-agnostic; supports hosted APIs and local Ollama; cost tracking (ADR-005) |
| Maths rendering | pandoc `--mathml`: regenerates MathML from LaTeXML's TeX annotation (texmath), TeX kept as annotation | The target Kindle renders MathML from personal documents acceptably (Q-3 device test); no extra tooling (ADR-006 rejected) |
| EPUB build | pandoc 3.x | Battle-tested HTML→EPUB3 conversion with TOC generation |
| EPUB validation | epubcheck (Java, in conversion image) | Industry-standard validator |
| PDF fallback | k2pdfopt | Purpose-built PDF reflow for e-readers |
| Images | Pillow | Greyscale conversion, resizing, dithering |
| Mail | stdlib `smtplib`; aiosmtplib once the worker is async (M1) | SMTP with STARTTLS; services are synchronous in M0, so no extra dependency yet |
| Settings | pydantic-settings | Typed configuration from env / secret files |
| Logging | stdlib `logging` in modules; structlog as the JSON formatter in the entry point (Q-13) | Structured, correlation IDs; modules need no logging library |
| Metrics | prometheus-client | Pull-based metrics |
| Tracing (optional) | OpenTelemetry SDK | Can be enabled later |
| Testing | pytest, pytest-asyncio, testcontainers, respx, hypothesis, syrupy | Unit, integration, contract, property and snapshot tests |
| Containers | Docker (multi-stage, non-root, distroless/slim) | Small attack surface |
| Orchestration | Docker Compose (phase 1) → k3s + Helm + Argo CD (phase 2) | Incremental adoption |
| IaC | Terraform (backups bucket, IAM, optional cloud env); Ansible (host configuration) | Reproducible infrastructure |
| CI/CD | GitHub Actions | Required by target roles; OIDC to cloud |


# 6. Detailed Design

## 6.1 Repository Structure

```
arx/
├── pyproject.toml              # uv-managed, ruff/mypy/pytest config
├── uv.lock
├── compose.yaml                # local development database
├── src/arx/
│   ├── bootstrap.py            # composition root (DI wiring)
│   ├── settings.py             # pydantic-settings
│   ├── domain/                 # entities, value objects, ranking, policies (pure)
│   │   ├── paper.py
│   │   ├── library.py
│   │   ├── ranking.py
│   │   └── delivery.py
│   ├── services/               # application use cases
│   │   ├── discovery.py
│   │   ├── library.py
│   │   ├── conversion.py
│   │   ├── delivery.py
│   │   └── admin.py
│   ├── adapters/
│   │   ├── arxiv/              # client, parsers, rate limiter
│   │   ├── embeddings/
│   │   ├── llm/
│   │   ├── conversion/         # html_cleaner, epub_builder, pdf_reflow
│   │   ├── mail/
│   │   ├── storage/            # file cache (local FS / object storage)
│   │   └── db/                 # SQLAlchemy models, repositories
│   ├── jobs/
│   │   ├── queue.py            # enqueue / dequeue / ack / retry
│   │   ├── scheduler.py        # cron-like schedules persisted in DB
│   │   ├── worker.py           # main loop, graceful shutdown
│   │   └── handlers/           # one module per job type
│   ├── api/                    # FastAPI routers (JSON)
│   ├── web/                    # HTMX routes, templates, static
│   └── observability/          # logging, metrics, tracing setup
├── migrations/                 # Alembic
├── tests/                      # mirrors src/arx/; level via markers (see 9.1)
│   ├── fixtures/               # recorded arXiv responses, golden EPUB inputs
│   └── evals/                  # LLM and ranking evaluation datasets
├── docker/
│   ├── Dockerfile.app          # api + worker image
│   └── Dockerfile.converter    # pandoc, epubcheck, k2pdfopt behind an internal HTTP API (6.5.4)
├── deploy/
│   ├── compose/                # docker-compose.yml, .env.example
│   ├── helm/arx/               # Helm chart
│   └── argocd/                 # Application manifests
├── infra/
│   ├── terraform/              # backup bucket, IAM/OIDC, optional cloud env
│   └── ansible/                # homelab host configuration
├── docs/
│   ├── spec/tds.md             # this document
│   ├── knowledge/              # OKF bundle; ADRs live in decisions/
│   ├── runbooks/
│   └── threat-model.md
└── .github/workflows/
```

Packages are created by the slice that first needs them; the tree above is the target, not a scaffold.

## 6.2 Data Model

### 6.2.1 Entity Overview

```
category 1---* subscription
paper *---* category              (paper_category)
paper 1---1 paper_embedding
paper 1---* paper_summary
paper 1---* feed_entry *---1 feed (one per date)
paper 1---* feedback
paper 1---0..1 library_item 1---* note
library_item *---* tag            (library_item_tag)
library_item *---* collection     (collection_item)
paper 1---* conversion *---1 kindle_profile
conversion *---* paper            (digest_part, digests only)
delivery *---* conversion         (delivery_item)
paper 1---0..1 digest_queue_item *---0..1 delivery
interest (seed statements, with embedding)
job, schedule, llm_usage, setting
```

### 6.2.2 Schema (DDL, abridged)

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE paper (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    arxiv_id        TEXT NOT NULL UNIQUE,              -- without version suffix
    latest_version  SMALLINT NOT NULL,
    title           TEXT NOT NULL,
    authors         JSONB NOT NULL,                    -- [{"name": "...", "affiliation": null}]
    abstract        TEXT NOT NULL,
    primary_category TEXT NOT NULL,
    doi             TEXT,
    journal_ref     TEXT,
    license         TEXT,
    published_at    TIMESTAMPTZ NOT NULL,
    updated_at      TIMESTAMPTZ NOT NULL,
    html_status     TEXT NOT NULL DEFAULT 'unknown'
                    CHECK (html_status IN ('unknown','available','unavailable')),
    html_checked_at TIMESTAMPTZ,
    search_tsv      TSVECTOR GENERATED ALWAYS AS (
                       setweight(to_tsvector('english', title), 'A') ||
                       setweight(to_tsvector('english', abstract), 'B')) STORED,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX paper_search_idx    ON paper USING GIN (search_tsv);
CREATE INDEX paper_published_idx ON paper (published_at DESC);

CREATE TABLE paper_category (
    paper_id    BIGINT REFERENCES paper(id) ON DELETE CASCADE,
    category    TEXT NOT NULL,
    PRIMARY KEY (paper_id, category)
);

CREATE TABLE paper_embedding (
    paper_id    BIGINT PRIMARY KEY REFERENCES paper(id) ON DELETE CASCADE,
    model       TEXT NOT NULL,
    embedding   VECTOR(384) NOT NULL
);
CREATE INDEX paper_embedding_hnsw ON paper_embedding
    USING hnsw (embedding vector_cosine_ops);

CREATE TABLE interest (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    statement   TEXT NOT NULL,
    weight      REAL NOT NULL DEFAULT 1.0,
    embedding   VECTOR(384) NOT NULL,
    active      BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE subscription (
    category    TEXT PRIMARY KEY,
    weight      REAL NOT NULL DEFAULT 1.0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE feedback (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    paper_id    BIGINT NOT NULL REFERENCES paper(id) ON DELETE CASCADE,
    signal      TEXT NOT NULL CHECK (signal IN
                  ('interesting','not_interesting','saved','sent','read')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE feed (
    feed_date   DATE PRIMARY KEY,
    ranker_version TEXT NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE feed_entry (
    feed_date   DATE REFERENCES feed(feed_date) ON DELETE CASCADE,
    paper_id    BIGINT REFERENCES paper(id) ON DELETE CASCADE,
    rank        SMALLINT NOT NULL,
    score       REAL NOT NULL,
    is_exploration BOOLEAN NOT NULL DEFAULT FALSE,
    explanation JSONB NOT NULL,          -- top contributing interests / papers
    PRIMARY KEY (feed_date, paper_id)
);

CREATE TABLE paper_summary (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    paper_id    BIGINT NOT NULL REFERENCES paper(id) ON DELETE CASCADE,
    summary     TEXT NOT NULL,
    why_relevant TEXT,
    model       TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (paper_id, prompt_version)
);

CREATE TABLE library_item (
    paper_id    BIGINT PRIMARY KEY REFERENCES paper(id) ON DELETE CASCADE,
    status      TEXT NOT NULL DEFAULT 'to_read'
                CHECK (status IN ('to_read','reading','read','archived')),
    added_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    read_at     TIMESTAMPTZ
);

CREATE TABLE tag (id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                  name TEXT NOT NULL UNIQUE);
CREATE TABLE library_item_tag (
    paper_id BIGINT REFERENCES library_item(paper_id) ON DELETE CASCADE,
    tag_id   BIGINT REFERENCES tag(id) ON DELETE CASCADE,
    PRIMARY KEY (paper_id, tag_id));

CREATE TABLE note (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    paper_id    BIGINT NOT NULL REFERENCES library_item(paper_id) ON DELETE CASCADE,
    body_md     TEXT NOT NULL,
    source      TEXT NOT NULL DEFAULT 'manual' CHECK (source IN ('manual','kindle')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE collection (id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                         name TEXT NOT NULL UNIQUE);
CREATE TABLE collection_item (
    collection_id BIGINT REFERENCES collection(id) ON DELETE CASCADE,
    paper_id      BIGINT REFERENCES library_item(paper_id) ON DELETE CASCADE,
    position      INT NOT NULL,
    PRIMARY KEY (collection_id, paper_id));

CREATE TABLE kindle_profile (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    width_px    INT NOT NULL,
    height_px   INT NOT NULL,
    image_dpi   INT NOT NULL DEFAULT 300,
    grayscale   BOOLEAN NOT NULL DEFAULT TRUE,
    is_default  BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE conversion (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    paper_id    BIGINT REFERENCES paper(id) ON DELETE CASCADE,   -- NULL for digests
    version     SMALLINT,
    profile_id  BIGINT NOT NULL REFERENCES kindle_profile(id),
    kind        TEXT NOT NULL CHECK (kind IN ('epub_html','pdf_reflow','digest')),
    converter_version TEXT NOT NULL,
    status      TEXT NOT NULL CHECK (status IN ('pending','succeeded','failed')),
    file_key    TEXT,                   -- storage key of output
    file_sha256 TEXT,
    file_bytes  BIGINT,
    diagnostics JSONB,                  -- epubcheck output, warnings
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX conversion_cache_key ON conversion
    (paper_id, version, profile_id, kind, converter_version)
    WHERE status = 'succeeded' AND paper_id IS NOT NULL;

CREATE TABLE digest_part (               -- papers bundled in a digest conversion
    conversion_id BIGINT REFERENCES conversion(id) ON DELETE CASCADE,
    paper_id      BIGINT REFERENCES paper(id) ON DELETE CASCADE,
    position      SMALLINT NOT NULL,
    PRIMARY KEY (conversion_id, paper_id));

CREATE TABLE delivery (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    recipient   TEXT NOT NULL,
    status      TEXT NOT NULL CHECK (status IN ('queued','converting','sending','sent','failed')),
    attempts    SMALLINT NOT NULL DEFAULT 0,
    last_error  TEXT,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    sent_at     TIMESTAMPTZ
);
CREATE TABLE delivery_item (
    delivery_id   BIGINT REFERENCES delivery(id) ON DELETE CASCADE,
    conversion_id BIGINT REFERENCES conversion(id) ON DELETE CASCADE,
    PRIMARY KEY (delivery_id, conversion_id));

CREATE TABLE digest_queue_item (
    paper_id    BIGINT PRIMARY KEY REFERENCES paper(id) ON DELETE CASCADE,
    added_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    delivery_id BIGINT REFERENCES delivery(id) ON DELETE SET NULL  -- digest in flight
);

CREATE TABLE llm_usage (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    purpose     TEXT NOT NULL,
    model       TEXT NOT NULL,
    input_tokens INT NOT NULL,
    output_tokens INT NOT NULL,
    cost_usd    NUMERIC(10,6) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

The job queue tables are specified in Section 6.3.

M0 implementation notes:

- The first Alembic migration creates only `paper`; the other tables, and `CREATE EXTENSION vector`, come with the slices that use them.
- `paper.primary_category` is nullable until the harvest (M1) fills it: `arx kindle` and `arx send` do not know it. The harvest slice backfills it and makes it `NOT NULL`.
- `authors` holds `{"name": …, "affiliation": null}` until a metadata source with affiliations is added.
- A paper is stored once per `arxiv_id` (FR-ING-07); storing it again is an upsert that replaces the row only with a newer version, so reruns change nothing (FR-ING-03). A newer version keeps `doi` and `journal_ref`, which the domain `Paper` does not carry yet, and resets `html_status` to `unknown` and `html_checked_at` to null, since HTML availability is per version.
- SQLAlchemy models in `adapters/db/models.py` mirror the migrations; an integration test fails when they differ.

### 6.2.3 Data Retention

| Data | Retention |
|---|---|
| Papers not in library, never surfaced in a feed | 90 days, then deleted (configurable) |
| Papers in a feed but not saved | 365 days |
| Library items, notes, tags | Indefinite |
| Papers in the digest queue | Kept while queued, whatever the rows above say |
| Papers carried by a sent delivery | Indefinite (keeps the *sent* marker of FR-DSC-08 and the delivery history of FR-DLV-05) |
| Conversion files (cache) | LRU eviction above configurable disk quota (default 10 GB). Eviction deletes the stored file and clears `file_key`, but keeps the `conversion`, `digest_part` and `delivery_item` rows (FR-DLV-05, FR-DSC-08) |
| Jobs (succeeded) | 14 days; failed jobs 90 days |
| Logs | 14 days on host |

## 6.3 Job Queue and Scheduler

### 6.3.1 Requirements

- Transactional enqueue (a job is enqueued in the same transaction as the business change that requires it).
- At-least-once execution; handlers MUST be idempotent.
- Per-queue concurrency limits (e.g. `arxiv` = 1, `convert` = 1, `llm` = 2, `default` = 2).
- Retries with exponential backoff and jitter; dead-letter state after `max_attempts`.
- Delayed execution (`run_after`) and job dependencies (`depends_on`).
- Crash recovery via lease expiry.
- Deduplication via optional `dedup_key`.

### 6.3.2 Schema

```sql
CREATE TABLE job (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    queue        TEXT NOT NULL,
    kind         TEXT NOT NULL,                 -- e.g. 'harvest', 'embed', 'convert'
    payload      JSONB NOT NULL,
    status       TEXT NOT NULL DEFAULT 'pending'
                 CHECK (status IN ('pending','running','succeeded','failed','dead','cancelled')),
    priority     SMALLINT NOT NULL DEFAULT 100,  -- lower = sooner
    attempts     SMALLINT NOT NULL DEFAULT 0,
    max_attempts SMALLINT NOT NULL DEFAULT 5,
    run_after    TIMESTAMPTZ NOT NULL DEFAULT now(),
    lease_until  TIMESTAMPTZ,
    locked_by    TEXT,
    depends_on   BIGINT REFERENCES job(id),
    dedup_key    TEXT,
    last_error   TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at  TIMESTAMPTZ
);
CREATE INDEX job_ready_idx ON job (queue, priority, run_after)
    WHERE status = 'pending';
CREATE UNIQUE INDEX job_dedup_idx ON job (dedup_key)
    WHERE dedup_key IS NOT NULL AND status IN ('pending','running');

CREATE TABLE schedule (
    name         TEXT PRIMARY KEY,               -- e.g. 'daily_harvest'
    cron         TEXT NOT NULL,                  -- evaluated in Europe/Warsaw
    job_kind     TEXT NOT NULL,
    payload      JSONB NOT NULL DEFAULT '{}',
    enabled      BOOLEAN NOT NULL DEFAULT TRUE,
    last_fired_at TIMESTAMPTZ
);
```

### 6.3.3 Dequeue Algorithm

```sql
WITH next AS (
    SELECT j.id
    FROM job j
    LEFT JOIN job d ON d.id = j.depends_on
    WHERE j.queue = $1
      AND j.status = 'pending'
      AND j.run_after <= now()
      AND (j.depends_on IS NULL OR d.status = 'succeeded')
    ORDER BY j.priority, j.run_after, j.id
    FOR UPDATE OF j SKIP LOCKED
    LIMIT 1
)
UPDATE job SET status = 'running',
               attempts = attempts + 1,
               locked_by = $2,
               lease_until = now() + $3::interval
FROM next WHERE job.id = next.id
RETURNING job.*;
```

- Workers wake on `LISTEN job_enqueued` (notified by an insert trigger) and additionally poll every 5 s as a safety net.
- Long-running handlers renew the lease (heartbeat) every `lease/3`.
- A reaper task resets jobs whose `lease_until < now()` and `status='running'` back to `pending` (crash recovery).
- On failure: `run_after = now() + min(cap, base * 2^attempts) * (1 ± 0.2 jitter)`; when `attempts >= max_attempts` → `dead`.
- If a dependency becomes `dead`/`cancelled`, dependants are cancelled transitively.
- Failure hook: a job kind MAY register a hook that runs in the same transaction as its own transition to `dead` or `cancelled`, including a transitive cancel. `build_digest` and `deliver` use it to mark their delivery `failed`, unless it is already `sent`, and release its digest queue items (6.5.3).
- Scheduler: a single loop evaluates `schedule` rows each minute, guarded by a PostgreSQL advisory lock so that only one scheduler fires even if two workers run; it enqueues with `dedup_key = '<name>:<fire_time>'`.
- Graceful shutdown: on SIGTERM the worker stops dequeuing, waits up to 30 s for running handlers, then releases leases.

### 6.3.4 Job Catalogue

| Kind | Queue | Payload | Idempotency key | Notes |
|---|---|---|---|---|
| `harvest` | arxiv | `{category, date}` | `harvest:<cat>:<date>` | Fetches listing, upserts papers |
| `fetch_paper` | arxiv | `{arxiv_id, queue?}` | `fetch:<id>`; `fetch_queue:<id>` with `queue: true` | On-demand import, idempotent (upsert; queue insert `ON CONFLICT DO NOTHING`); `queue: true` inserts the `digest_queue_item` in the upsert's transaction (FR-DLV-08) |
| `probe_html` | arxiv | `{paper_id, version}` | `probe:<id>:<ver>` | Determines HTML availability |
| `embed` | default | `{paper_ids[]}` | — (upsert) | Batched (32) |
| `rank` | default | `{date}` | `rank:<date>` | Builds feed |
| `summarize` | llm | `{paper_id, prompt_version}` | `sum:<id>:<pv>` | Budget-checked |
| `convert` | convert | `{paper_id, version, profile_id, kind}` | cache key | See 6.5 |
| `digest` | default | `{fire_time}` | `scheduled_digest:<fire_time>` (`<name>:<fire_time>`, 6.3.3) | Fired by the `scheduled_digest` schedule row, seeded from `ARX_DIGEST_CRON` (FR-DLV-04); claims the digest queue, see 6.5.3 |
| `build_digest` | convert | `{delivery_id, profile_id, paper_ids[]?}` (`paper_ids` only for the ad-hoc digest) | `build_digest:<delivery_id>` | Writes conversion, `digest_part` and `delivery_item` rows; splits oversized digests (6.5.3) |
| `deliver` | default | `{delivery_id}` | `deliver:<id>` | SMTP |
| `backup` | default | `{}` | `backup:<date>` | pg_dump → encrypt → upload |
| `maintenance` | default | `{}` | `maint:<date>` | Retention, cache eviction, VACUUM hints |

## 6.4 Discovery and Ranking

### 6.4.1 Inputs

- Candidate set *C*: papers published in the feed window (default: last announcement day) in subscribed categories, excluding papers already in the library or with `not_interesting` feedback.
- Seed interests *I* = {(e<sub>i</sub>, w<sub>i</sub>)}: embedding and weight per active interest statement.
- Positive history *P*: embeddings of papers with signals `interesting`, `saved`, `sent`, `read` (most recent 500, time-decayed).
- Negative history *N*: embeddings of papers marked `not_interesting` (most recent 500).
- Category weights from `subscription.weight`.

### 6.4.2 Scoring Function (ranker v1)

For a candidate paper with embedding *x* and categories *K*:

```
s_interest = max_i ( w_i * cos(x, e_i) )
s_history  = mean of top-5 cos(x, p) over p in P, each weighted by decay(age_p)
s_negative = max over n in N of cos(x, n)
s_category = max_k weight(k) for k in K, normalised to [0, 1]

score = 0.45 * s_interest
      + 0.35 * s_history
      + 0.10 * s_category
      - 0.30 * max(0, s_negative - 0.80)
      + 0.10 * novelty_bonus          # paper not similar to anything in library

decay(age) = 0.5 ^ (age_days / 60)    # half-life 60 days
```

- Coefficients are configuration values, versioned as `ranker_version`.
- **Cold start:** with fewer than 10 positive signals, `s_history` weight is redistributed to `s_interest`.
- **Exploration:** 10% of feed slots (rounded down, min. 1 when *N* ≥ 10) are filled by uniformly sampling candidates ranked 50–300, marked `is_exploration = true`.
- **Explanation:** the arguments of the max/top-k terms (interest statement or past paper title) are stored in `feed_entry.explanation` and displayed in the UI (FR-DSC-04).

### 6.4.3 Evaluation

- The owner's feedback is logged; offline evaluation computes precision@10 and nDCG@20 of the ranker on the last 30 days of feedback whenever coefficients change.
- A ranker change MUST NOT be merged if precision@10 on the evaluation set drops by more than 5 percentage points (CI job `eval-ranker`, see 9.4).

## 6.5 Conversion Pipeline

The default Kindle profile (Q-1) is `paperwhite-11-signature`: Kindle Paperwhite Signature Edition (11th generation), 1236 × 1648 px, `image_dpi` 300, greyscale. The migration that creates `kindle_profile` seeds it with `is_default = TRUE`. Margins subtracted from the figure width (6.5.1 step 5) are tuned on the device.

### 6.5.1 HTML → EPUB (primary path)

| Step | Operation | Details |
|---|---|---|
| 1 | Fetch | GET HTML rendition and its assets (images, CSS ignored). URL allowlist: arXiv HTML host only. Rate-limited through the arXiv limiter. Max response size 25 MB; timeout 60 s. |
| 2 | Sanitise | Parse with lxml; remove scripts, iframes, forms, event handlers, external links in `src`; normalise with nh3 allowlist, which MUST include the MathML elements and attributes LaTeXML emits (FR-CNV-02). |
| 3 | Clean structure | Remove arXiv page chrome (header, footer, navigation, "report issue" widgets, theme toggles). Keep `<article>` content without the LaTeXML front matter the title page repeats (title, authors, abstract). Normalise heading levels (h1 = title, h2 = sections; deferred from M0 to M1). |
| 4 | Mathematics | Keep LaTeXML's MathML with its `application/x-tex` annotation. In step 9 pandoc regenerates MathML from that TeX (texmath) and writes it into the EPUB with the TeX as annotation (Q-3). Where texmath cannot parse an expression (e.g. author macros), pandoc keeps the TeX source as text and warns; the warning is logged. |
| 5 | Figures | Download, convert to 8-bit greyscale, resize to profile width minus margins, optionally apply Floyd–Steinberg dithering for line art. Keep captions. |
| 6 | Tables | Measure column count/estimated width; tables exceeding the threshold are rendered to PNG (headless rendering in converter image); others kept as HTML with compact CSS. |
| 7 | References & links | Convert in-document citations to internal EPUB links; strip external hyperlinks except DOI/arXiv links in references. |
| 8 | Front matter | Generate title page: title, authors, arXiv ID + version, dates, licence, abstract, LLM summary (if any, clearly labelled). |
| 9 | Build | `pandoc --from html --to epub3 --toc --toc-depth=2 --mathml --epub-title-page=false --css kindle.css --metadata lang=en --metadata …` (step 8 supplies the title page) |
| 10 | Validate | Run `epubcheck`; errors → `conversion.status = failed` with diagnostics; warnings stored. |
| 11 | Store | Write to storage under `conversions/<arxiv_id>/v<ver>/<profile>/<converter_version>.epub`; record SHA-256 and size. |

### 6.5.2 PDF Reflow (fallback path)

1. Download the PDF (rate-limited, size limit 50 MB).
2. Run `k2pdfopt` with profile-derived parameters (device width/height, DPI, column detection on, margins trimmed).
3. Validate output opens with `pypdf`; record page count.
4. Mark output as `kind = pdf_reflow`; the UI indicates reduced quality.

### 6.5.3 Digest

Concatenate cleaned HTML of N papers (each as a top-level part with its own title page), then build one EPUB with a two-level table of contents. Hard limit: total size under the delivery limit; otherwise split into multiple digests.

Digest queue (FR-DLV-04, FR-DLV-08, M1):

- The `digest` job works in one transaction. It removes unclaimed queue items whose `html_status` is `unavailable` and reports them (see below). It then takes the remaining unclaimed items (`digest_queue_item.delivery_id IS NULL`) in `added_at` order; `unknown` counts as sendable until `build_digest` tries the rendition. If none remain, the job ends without a delivery. Otherwise, in the same transaction, it creates the `delivery` row, sets `delivery_id` on the taken items, enqueues `build_digest` with the dependent `deliver`, and marks itself succeeded, so a retry cannot create a second delivery (NFR-07). Papers queued later, and papers claimed by a digest still in flight, wait for the next run.
- The recipient is `ARX_DIGEST_RECIPIENT` (12), which must be on the allowlist (FR-DLV-07).
- `build_digest` (payload `{delivery_id, profile_id}`, plus `paper_ids[]` for the ad-hoc digest below) reads its papers from the queue items claimed by that delivery. In one transaction it creates the digest conversion(s), `digest_part` rows and `delivery_item` rows.
- A paper whose rendition turns out to be missing (`unknown` → 404) is marked `unavailable`, left out, removed from the queue and reported.
- When the papers exceed `ARX_DELIVERY_MAX_BYTES`, the digest is split, in queue order, into several EPUBs. The first part keeps the claimed delivery and its already-enqueued `deliver` job. Each further part gets a new `delivery` and `deliver` job, and its items are re-pointed to that delivery, all in the same transaction.
- When no paper remains, `build_digest` marks the delivery `failed` with that reason, and the `deliver` job for that delivery ends without sending.
- Retry (FR-DLV-06, FR-ADM-02): retrying a failed single-paper delivery resets it to `queued` and enqueues a new `deliver`. A failed digest is not retried, because its papers are back in the queue for the next run. Job retry (FR-ADM-02) is likewise refused (409) for `build_digest` and for the `deliver` of a digest delivery, so a released paper can't be sent twice.
- A conversion with `file_key` NULL (file evicted, 6.2.3) is a cache miss. `convert` regenerates the file into the same row, and a retried `deliver` enqueues `convert` first when the file is gone.
- When a delivery reaches `sent`, its queue items are deleted in the same transaction. After a permanent failure they are released, so they stay queued for the next run. This includes a `build_digest` or `deliver` job that ends `dead` or `cancelled`: the failure hook (6.3.3) marks the delivery `failed` and releases its items.
- The ad-hoc digest (`POST /api/v1/deliveries` with `digest: true`) creates its own delivery and passes its papers as `paper_ids[]` in the `build_digest` payload, outside the queue.
- A paper whose EPUB alone exceeds `ARX_DELIVERY_MAX_BYTES` cannot be split. It is left out, removed from the queue, and named in the digest's message body and in the delivery's `last_error`, so it doesn't fail every later run (FR-DLV-03).
- Until the PDF path (FR-CNV-05), a paper without an HTML rendition is removed from the queue at the run, not kept for later. Removed papers, whether unavailable or too large, are reported with their arXiv ID and reason. The report goes in the digest's message body and in the `last_error` of the run's delivery (the first part's delivery when split). When the run sends nothing, it goes in the `digest` job's `last_error` instead. The Deliveries view, `GET /api/v1/digest/queue` and `arx queue list` show the last run's removed papers from that source.
- M1 commands: `arx queue add REF`, `arx queue list` and `arx queue remove REF`; the feed card gets a *Queue* button. `arx queue add` imports an unknown paper synchronously (FR-ING-04) before queueing it; the API enqueues `fetch_paper` with `queue: true` instead.
- Removing a claimed item (digest in flight) is refused (API 409). Re-adding a paper that is still claimed changes nothing; once that delivery is sent the paper leaves the queue.

### 6.5.4 Isolation

Conversion tools (pandoc, k2pdfopt, epubcheck) run in a dedicated, long-running **converter** container (own image) that serves a narrow internal HTTP API; the worker is its only client (Q-8). A request carries everything one conversion step needs (the prepared HTML with its images, or the PDF, plus the profile parameters); the response carries the output file or the tool's diagnostics, so no volume is shared. The worker does all fetching (steps 1 and 5), so the converter has no database credentials and no outbound network access. The same image and API run in both phases: in Compose a `converter` service on an internal network shared only with the worker, with no published port (11.1); in k3s its own Deployment behind a ClusterIP Service (11.2), because NetworkPolicies apply per Pod and the worker needs egress. Each request has CPU time, memory (`ulimit`/cgroup) and wall-clock limits. Until the worker exists, M0 runs pandoc as a local subprocess of the CLI.

## 6.6 Integrations

### 6.6.1 arXiv

| Use | Interface | Notes |
|---|---|---|
| Daily listing | RSS/Atom feeds per category or API query by `submittedDate` *(verify which is more reliable; M0 uses RSS, Q-2)* | Configurable base URLs |
| Metadata lookup | arXiv API (`/api/query?id_list=`) | Batch up to 100 IDs per request |
| Keyword search | arXiv API (`/api/query?search_query=&start=&max_results=&sortBy=relevance`) | One request per result page; FR-DSC-08 |
| HTML availability | `GET`/`HEAD` on HTML rendition URL | 404 → `unavailable` |
| Full text | HTML rendition; PDF | For conversion only |

Client requirements:

- One shared async client per worker, `max_connections = 1`, explicit `User-Agent` identifying the application and a contact e-mail.
- **Rate limiter:** a token bucket with capacity 1 and refill interval 3 s *(configurable)*, implemented in-process and additionally guarded by a PostgreSQL advisory lock so that a second worker instance or a CLI process (`arx search`) cannot violate the limit: the holder sends one request and keeps the lock until the interval after it has passed.
- Retries on 429/5xx/network errors with backoff (max 5); respect `Retry-After`.
- M0 exception: the manual walking-skeleton script makes a handful of sequential requests and waits the configured interval between them instead of using the limiter; the limiter replaces the wait in M1.
- M0 command (FR-ING-04, FR-DLV-01): `arx kindle REF --to ADDR` accepts an arXiv ID (`2401.01234`, `2401.01234v2`, `arXiv:…`, old-style `hep-th/9901001`) or an `arxiv.org/abs|pdf|html/…` URL; without a version it takes the latest. It checks the recipient first, looks the paper up with `id_list`, downloads `arxiv.org/html/<id>v<n>`, converts (6.5.1) and mails (6.6.3). An unknown paper or a 404 rendition exits with status 1 and the reason; the PDF path (FR-CNV-05) follows later. The API carries no licence, so the title page omits it until a source that has it is added. Requests use a synchronous client that follows redirects until the async worker (M1); endpoints are fixed until `ARX_ARXIV_*_BASE` arrive in M1.
- M0 command (FR-ING-02, partial: one category, manual, nothing stored): `arx today CATEGORY` checks the category code (archive or `archive.subject`, e.g. `cs.LG`, `hep-th`, `cond-mat.mtrl-sci`) before any request, reads `rss.arxiv.org/rss/<category>` through the same spaced client and prints one line per paper: versioned ID, `[cross]` for cross-lists, title, first author. Items announced as `replace` or `replace-cross` are left out, since they are new versions of older papers. Author affiliations in parentheses are dropped. A feed without items (weekends, holidays) prints a one-line note and exits with status 0; a malformed category, an unknown one (arXiv answers 400) or a failed request exits with status 1 and a one-line reason. RSS is the M0 stopgap for Q-2; the M1 spike still compares it with the API date query.
- Keyword search (FR-DSC-08, M1 after the `paper` table exists): `arx search TERMS… [--start N] [--limit N]` turns plain terms into `all:` terms joined with `AND` and passes terms with a field prefix (`ti:`, `au:`, `abs:`, `cat:`) through unchanged; `--limit` defaults to 20, at most 50. Each page is one API request through the shared rate limiter, including its advisory lock, so an interactive search never runs closer than the configured interval to a worker request (NFR-16). Results are not stored; the marker comes from one lookup of the page's arXiv IDs (without version) in `paper`, `library_item` (from M3; M1 has no library table) and the conversions of sent deliveries (`conversion.paper_id`, or `digest_part` for digests). Output is one line per result: versioned ID, marker, title, first author, year; the owner sends or queues a result with `arx kindle ID` or `arx queue add ID`, which import it (FR-ING-04). A malformed query (API error entry) exits with status 1 and the reason. The UI Search view (6.8) follows in M3.
- Response parsing is covered by contract tests on recorded fixtures (see 9.2).
- Metric `arx_arxiv_requests_total{endpoint,status}` and histogram of inter-request spacing.

### 6.6.2 LLM Gateway

- All LLM calls go through `LlmGateway` (Protocol) implemented with LiteLLM; provider and model are configuration.
- Only public data (title, abstract, optionally section headings) is sent to hosted providers.
- **Budget guard:** before each call the gateway checks month-to-date spend from `llm_usage`; if the projected cost would exceed the cap, the call is skipped and the job succeeds with `summary = null` (graceful degradation, NFR-14).
- Prompts are versioned files under `src/arx/adapters/llm/prompts/` with a `prompt_version` constant; any change to a prompt requires a version bump and passing the evaluation suite (9.5).
- Outputs are validated against a Pydantic schema (structured output / JSON mode); invalid outputs are retried once, then discarded.
- Optional local backend: Ollama on the owner's laptop, used when reachable (health-checked), for zero-cost experimentation.

### 6.6.3 Send to Kindle (SMTP)

- Transport: SMTP submission with STARTTLS (587) or implicit TLS (465); credentials via secret. M0 implements STARTTLS only; the password file is read on every send, so a rotated secret needs no restart.
- Provider (Q-4): a dedicated Gmail account used only by Arx, `smtp.gmail.com:587` with STARTTLS and an app password. Gmail limits attachments to 25 MB *(verify)*, below the 50 MB that Send to Kindle accepts, so the Gmail limit sets `ARX_DELIVERY_MAX_BYTES`: 20 MiB of raw file, because base64 encoding grows the message by about a third and the limit may apply to the encoded size. Switching to a transactional provider (own domain with SPF/DKIM) changes configuration only.
- The sender address MUST be on the Amazon "Approved Personal Document E-mail List"; recipient MUST be in `ARX_DELIVERY_ALLOWED_RECIPIENTS`. Addresses are compared case-insensitively; settings refuse to load when the list is empty or holds an address outside `@kindle.com`.
- Message: plain-text body with paper titles; subject is the title on one line; attachment with RFC 2231-encoded filename `<first-author>-<year>-<short-title>.epub` (ASCII-safe): the first author's last name, the year first published and the first five title words, accents folded to ASCII, lower-case, other characters dropped, joined with hyphens, at most 80 characters. The versioned arXiv ID (`/` replaced by `-`) stands in when the author name has no ASCII letters.
- Size check of the raw file before sending against `ARX_DELIVERY_MAX_BYTES` *(default 20 MiB, verify)*; a larger file is rejected without connecting, with its size and the limit in the message. The downscale option (FR-DLV-03) follows in M1 with image processing.
- Outcome tracking: SMTP acceptance is recorded as `sent`; Amazon does not provide delivery confirmation to the application.
- M0 command: `arx send FILE.epub --to ADDR --id 2401.01234v2 --title T [--author A ...] --published YYYY-MM-DD` mails one EPUB; the flags stand in for the paper metadata until the arXiv client looks it up. Rejections, invalid settings and SMTP errors exit with status 1 and a one-line reason.

## 6.7 API Specification

All JSON endpoints are under `/api/v1`, documented via generated OpenAPI. HTML (HTMX) routes mirror the same services.

| Method | Path | Description | Req. |
|---|---|---|---|
| GET | `/api/v1/feed?date=&min_score=&category=` | Ranked feed for a date | FR-DSC-02/05 |
| POST | `/api/v1/papers/{id}/feedback` | Body: `{signal}` | FR-DSC-03 |
| GET | `/api/v1/papers/{id}` | Paper detail incl. summary, conversions, library state | — |
| GET | `/api/v1/papers/{id}/similar?limit=` | More like this | FR-DSC-07 |
| POST | `/api/v1/papers/import` | Body: `{reference}` (ID or URL) → 202 + job id | FR-ING-04 |
| GET | `/api/v1/search?q=&start=&limit=` | Keyword search of arXiv, each result with its in-Arx marker (*sent* / *stored* in M1) | FR-DSC-08 |
| GET | `/api/v1/library?status=&tag=&collection=&q=&mode=keyword\|semantic` | Library listing & search | FR-LIB-01/04 |
| PUT | `/api/v1/library/{paper_id}` | Upsert library item (status) | FR-LIB-01 |
| DELETE | `/api/v1/library/{paper_id}` | Remove from library | — |
| PUT | `/api/v1/library/{paper_id}/tags` | Replace tag set | FR-LIB-02 |
| POST/PATCH/DELETE | `/api/v1/library/{paper_id}/notes[/{note_id}]` | Notes CRUD | FR-LIB-03 |
| GET/POST/PATCH/DELETE | `/api/v1/collections[/{id}]` | Collections CRUD | FR-LIB-05 |
| GET | `/api/v1/library/export?format=bibtex\|json` | Export | FR-LIB-06 |
| POST | `/api/v1/conversions` | Body: `{paper_id, profile_id?}` → 202 | FR-CNV-* |
| GET | `/api/v1/conversions/{id}/file` | Download output | FR-CNV-10 |
| POST | `/api/v1/deliveries` | Body: `{paper_ids[], profile_id?, digest: bool}` → 202; `digest` sends the papers now as one digest, outside the queue | FR-DLV-01, FR-CNV-07 |
| GET | `/api/v1/deliveries?status=` | History | FR-DLV-05 |
| GET/POST | `/api/v1/digest/queue` | List the digest queue and the last run's removed papers (6.5.3); body `{reference}` (ID or URL) queues a paper, importing it first if unknown (202 + job id; `fetch_paper` with `queue: true`); a known paper → 201, one already queued → 200 (idempotent) | FR-DLV-08 |
| DELETE | `/api/v1/digest/queue/{paper_id}` | Remove from the digest queue; 409 while a digest in flight claims it | FR-DLV-08 |
| GET/PUT | `/api/v1/settings/{section}` | Subscriptions, interests, schedules, profiles, delivery, llm | FR-ADM-01 |
| GET | `/api/v1/jobs?status=&kind=` | Job monitor | FR-ADM-02 |
| POST | `/api/v1/jobs/{id}/retry` · `/cancel` | Job control; retry → 409 for `build_digest` and a digest's `deliver` (6.5.3) | FR-ADM-02 |
| GET | `/api/v1/usage/llm?month=` | Spend vs. budget | FR-ADM-03 |
| GET | `/healthz`, `/readyz` | Probes (unauthenticated, no data) | FR-ADM-04 |
| GET | `/metrics` | Prometheus (bound to internal interface / NetworkPolicy) | NFR-17 |

Conventions:

- Errors use RFC 9457 Problem Details (`application/problem+json`).
- Asynchronous operations return `202 Accepted` with `Location` of the created resource and `job_id`.
- Pagination: cursor-based (`?cursor=&limit=`, max 100).
- Mutating endpoints accept `Idempotency-Key` header; keys stored 24 h.

## 6.8 Web UI

| View | Content | Key interactions |
|---|---|---|
| Today | Ranked cards: title, authors (first 3), categories, score badge, plain-language summary, "why" line, HTML availability icon | Interesting / Not interesting, Save, Send to Kindle, Queue for digest, expand abstract |
| Paper | Full metadata, abstract, summary, similar papers, conversions, delivery history, notes | Convert, download, send, tag, note |
| Library | Filterable list (status, tag, collection), search box with keyword/semantic toggle | Bulk status change, add to collection, send as digest, queue for digest |
| Search | Keyword search of all of arXiv (FR-DSC-08); cards like Today with a *sent* / *library* / *stored* badge | Import, Send to Kindle, Queue for digest, next page |
| Deliveries | History with status and errors; the digest queue with the next scheduled run and the last run's removed papers | Retry (single-paper deliveries only), remove from queue |
| Settings | Subscriptions, interests (with live preview of matching recent papers), schedules, Kindle profiles, delivery, LLM budget | — |
| Jobs | Queue state, failures with stack-trace excerpt | Retry (not for `build_digest` or a digest's `deliver`), cancel |

Implementation notes: server-rendered Jinja templates; HTMX for partial updates; no client-side framework; total JS < 50 kB; CSRF token on all forms; works without JavaScript for read-only views.


# 7. Security

## 7.1 Security Objectives

1. Confidentiality of credentials (SMTP, LLM API key, cloud credentials, session secret).
2. Integrity of the host: untrusted input (arXiv HTML/PDF, LLM output) cannot lead to code execution or lateral movement.
3. Availability: bugs or malicious content cannot exhaust host resources shared with other homelab services.
4. Supply-chain integrity of the deployed artefacts.

## 7.2 Threat Model (STRIDE summary)

| # | Threat | Asset / Entry point | Mitigation |
|---|---|---|---|
| T1 | Spoofing — unauthorised access to UI/API | Web UI | Tailnet-only exposure, the only control in M1–M2 (Q-7); from M3 owner login (FR-ADM-05: Argon2id password hash + session cookie: `Secure`, `HttpOnly`, `SameSite=Strict`); optional Tailscale identity headers check |
| T2 | Tampering — malicious HTML/SVG in paper content (XSS, XXE) | Conversion pipeline, UI rendering | nh3 sanitisation; lxml with `resolve_entities=False`, `no_network=True`; templates autoescape; CSP `default-src 'self'` |
| T3 | Tampering / EoP — exploit in pandoc, k2pdfopt, image libraries via crafted files | Converter | Isolated converter container: non-root, read-only rootfs, no egress, ingress from the worker only, seccomp default, dropped capabilities, CPU/memory/time limits; images scanned and pinned by digest |
| T4 | SSRF via user-supplied import URL or embedded asset URLs | Import endpoint, figure fetcher | Strict parser accepting only arXiv ID patterns / allowlisted hosts; resolved IP must be public; redirects re-validated |
| T5 | Repudiation | Admin actions | Structured audit log of settings changes and deliveries |
| T6 | Information disclosure — secrets in repo, image layers or logs | Git, CI, logs | gitleaks pre-commit + CI; secrets only as mounted files; log redaction filter; no secrets in image layers (checked by Trivy secret scanner) |
| T7 | Information disclosure — prompt injection in paper abstracts influencing LLM | LLM enrichment | LLM has no tools and no secrets in context; output schema-validated and rendered as escaped text; agent (P2) tools are read-only |
| T8 | DoS — oversized documents, decompression bombs, pathological maths | Converter, worker | Size limits, Pillow `MAX_IMAGE_PIXELS`, per-job timeouts, per-queue concurrency, cgroup limits |
| T9 | Abuse of mail relay | Delivery | Recipient allowlist; rate limit 20 deliveries/hour |
| T10 | Supply chain — compromised dependency or base image | Build | Locked dependencies with hashes (`uv.lock`), Dependabot/Renovate, SBOM, image signing (cosign), signature verification at deploy (phase 2) |
| T11 | Data loss / ransomware on host | Database | Encrypted off-site backups with object lock / versioning; restore tests |

The full threat model is maintained in `docs/threat-model.md` and reviewed at each milestone.

## 7.3 Secure SDLC Controls

| Stage | Control | Tool | Gate |
|---|---|---|---|
| Pre-commit | Secrets, lint, format, types | gitleaks, ruff, mypy | Block commit |
| Pull request | SAST | SonarCloud (quality gate), Semgrep (OWASP + Python rules), Bandit | Block merge on new critical/high or failed quality gate |
| Pull request | Dependency vulnerabilities (SCA) | `pip-audit`, Trivy fs | Block on critical; high requires justification |
| Build | Image vulnerability & misconfiguration scan | Trivy image, Hadolint | Block on critical (NFR-10) |
| Build | SBOM generation | Syft (CycloneDX), attached as artefact and attestation | — |
| Build | Image signing & provenance | cosign keyless (GitHub OIDC), SLSA provenance via GitHub attestations | — |
| Deploy (phase 2) | Policy | Kyverno: require signed images, non-root, resource limits, no `latest` tag | Reject non-compliant manifests |
| Post-deploy | DAST | OWASP ZAP baseline + API scan (OpenAPI) against staging | Block promotion on high-risk alerts |
| IaC | Misconfiguration scanning | Checkov or Trivy config on Terraform/Helm | Block on high |
| Continuous | Dependency updates | Renovate | Weekly |

## 7.4 Secrets Management

- Phase 1 (Compose): Docker secrets mounted as files under `/run/secrets`; `.env` holds only non-secret configuration.
- Phase 2 (k3s): Sealed Secrets (or SOPS + age) committed to Git in encrypted form; decrypted only in-cluster.
- Cloud access from CI: GitHub Actions OIDC federation (AWS IAM role or Azure workload identity federation); **no long-lived cloud keys** in CI.
- Backup encryption: `age` public key on the host; private key stored offline by the owner.

## 7.5 Container Hardening Baseline

- Base images: `python:3.14-slim` (app, multi-stage, build tools excluded from final layer) or distroless where feasible; pinned by digest.
- Run as UID ≥ 10000; read-only root filesystem with explicit writable `tmpfs`/volumes.
- `cap_drop: [ALL]`, `no-new-privileges`, default seccomp profile.
- Health checks defined in Dockerfile and Compose/Helm.


# 8. Observability and Operations

## 8.1 Logging

- Modules log through `logging.getLogger(__name__)`; the entry point installs structlog's `ProcessorFormatter` on the root handler (Q-13). Plain stdlib formatting is enough until the slice that needs JSON output.
- JSON logs via structlog to stdout; fields: `ts`, `level`, `event`, `logger`, `request_id` or `job_id`, `job_kind`, `paper_id`, `duration_ms`, `error.type`.
- Redaction processor removes values of keys matching `password|token|secret|authorization|api_key`.
- Phase 1: Docker log rotation (10 MB × 5). Phase 2: optional Loki with 14-day retention if memory allows.

## 8.2 Metrics

| Metric | Type | Labels |
|---|---|---|
| `arx_http_requests_total` | counter | `route`, `method`, `status` |
| `arx_http_request_duration_seconds` | histogram | `route` |
| `arx_jobs_total` | counter | `kind`, `outcome` |
| `arx_job_duration_seconds` | histogram | `kind` |
| `arx_jobs_pending` | gauge | `queue` |
| `arx_job_oldest_pending_age_seconds` | gauge | `queue` |
| `arx_arxiv_requests_total` | counter | `endpoint`, `status` |
| `arx_arxiv_request_spacing_seconds` | histogram | — |
| `arx_conversions_total` | counter | `kind`, `outcome` |
| `arx_epubcheck_errors_total` | counter | — |
| `arx_deliveries_total` | counter | `outcome` |
| `arx_llm_cost_usd_total` | counter | `model`, `purpose` |
| `arx_llm_budget_remaining_usd` | gauge | — |
| `arx_feed_size` | gauge | — |
| `arx_last_successful_harvest_timestamp` | gauge | `category` |

## 8.3 Alerts

| Alert | Condition | Severity |
|---|---|---|
| HarvestStale | `time() - arx_last_successful_harvest_timestamp > 36h` | warning |
| QueueBacklog | `arx_job_oldest_pending_age_seconds{queue!="arxiv"} > 1800` | warning |
| JobsDead | increase of `arx_jobs_total{outcome="dead"}` > 0 in 1h | warning |
| DeliveryFailures | ≥ 3 failed deliveries in 24 h | critical |
| ArxivRateViolation | any `arx_arxiv_request_spacing_seconds` bucket below configured interval | critical |
| LlmBudgetLow | budget remaining < 20% | info |
| BackupMissing | no successful `backup` job in 26 h | critical |
| ServiceDown | `/readyz` failing for 5 min (Uptime Kuma / blackbox exporter) | critical |

Notification channel: Uptime Kuma (phase 1) and Alertmanager → ntfy or Telegram push (phase 2).

## 8.4 Dashboards

Grafana dashboards (provisioned as code under `deploy/observability/`):

1. **Service health** — request rate, latency percentiles, error rate, readiness.
2. **Pipeline** — jobs by kind/outcome, queue depth, oldest pending, harvest freshness per category.
3. **Conversion quality** — success rate by kind, epubcheck errors, PDF-fallback share, median conversion time.
4. **Reading** — papers surfaced/saved/sent/read per week, feedback ratio, LLM spend.

## 8.5 Runbooks

Runbooks in `docs/runbooks/` MUST exist for: harvest stale; queue backlog; conversion failures spike; delivery failures (SMTP auth, Amazon rejection); database restore; rotating secrets; host disk pressure.

## 8.6 Resource Budget (M710q, 8 GB RAM)

| Component | Memory request / limit | CPU limit |
|---|---|---|
| PostgreSQL 17 (`shared_buffers=256MB`) | 512 MB / 1 GB | 1.0 |
| api (Uvicorn, 1 worker) | 192 MB / 384 MB | 0.5 |
| worker (incl. embedding model ~150 MB) | 512 MB / 1.25 GB | 1.5 |
| converter | 256 MB / 1 GB (burst) | 1.0 |
| Phase 2 additions: k3s control plane | ~600 MB | — |
| Prometheus (retention 7d) + Grafana | 384 MB + 192 MB | 0.5 |
| **Total (phase 2, peak)** | **≈ 5 GB** | |

Headroom is reserved for the OS, Dockhand, Uptime Kuma and other homelab workloads. Exceeding limits MUST trigger OOM-kill and job retry rather than host-level memory pressure.


# 9. Testing Strategy

## 9.1 Approach

Development follows **test-driven development** in every layer: each behaviour change starts with a failing test, and a bug fix's first test reproduces the bug. Exceptions:

- Trivial changes (renames, documentation, configuration values that do not change specified behaviour) need no new test.
- Template markup needs no test-first unit test; the route or handler behind it is still test-first, and the end-to-end UI smoke flows (Section 9.2) cover rendering after merge.
- Migrations are covered by integration tests written after the migration.

Agents implement all code test-first, core mechanisms (job queue, rate limiter, ranking, conversion pipeline) included. Review is agentic: every merge request passes the `mr-reviewer` agent, and the owner raises questions and adjustments.

Red, green and refactor steps are not separate commits, and commit messages and merge requests do not name them: a commit holds one behaviour with its tests, all checks green.

Each functional requirement maps to at least one automated test referencing its ID (e.g. `@pytest.mark.req("FR-CNV-08")`); a CI step reports requirement coverage.

Test files mirror `src/arx/` (e.g. `src/arx/jobs/queue.py` → `tests/jobs/test_queue.py`). The test level is a pytest marker, not a folder: unmarked tests are unit tests; `integration`, `contract` and `golden` mark the other levels. Markers are registered in `pyproject.toml` and enforced with `--strict-markers`. Shared inputs live in `tests/fixtures/`; evaluation datasets in `tests/evals/`.

## 9.2 Test Levels

| Level | Marker | Scope | Tooling | Runs |
|---|---|---|---|---|
| Unit | — | Domain (ranking maths, state transitions, parsers, policies) | pytest, hypothesis (property tests for queue backoff, ranking invariants) | Every commit |
| Integration | `integration` | Repositories, job queue semantics (SKIP LOCKED concurrency, lease expiry, dependencies), migrations | pytest + testcontainers (PostgreSQL + pgvector) | Every PR |
| Contract | `contract` | arXiv response parsing against recorded fixtures; HTTP behaviour (rate limiting, retries) | respx, recorded Atom/HTML fixtures refreshed monthly by a scheduled workflow | Every PR |
| Conversion (golden) | `golden` | 15–25 representative papers (heavy maths, wide tables, many figures, no HTML) → EPUB; structure snapshot + epubcheck pass | syrupy snapshots, epubcheck | Every PR touching conversion |
| End-to-end | — (separate suite) | Compose stack; import → convert → deliver to a test SMTP server (Mailpit) | pytest + httpx; Playwright for 3–5 UI smoke flows | Main branch, nightly |
| Security | — | SAST, SCA, DAST (Section 7.3) | — | PR / post-deploy |
| Performance | — | Feed and search latency with 50 000 synthetic papers | Locust or k6 | Before each milestone release |
| Resilience | — | Kill worker mid-job, restart DB, SMTP outage | Scripted chaos tests in E2E environment | Milestone releases |

## 9.3 Key Test Cases (non-exhaustive)

- Two concurrent workers never execute the same job (integration, 1 000 jobs, assert unique executions).
- An expired lease causes re-execution; handler idempotency prevents duplicate side effects (e.g. no duplicate delivery e-mail).
- The arXiv client never issues two requests within the configured interval under concurrent callers (property test with fake clock).
- Re-harvesting the same day produces zero new rows.
- Malicious HTML fixture (script tags, `javascript:` URLs, XXE payload, SVG with external references) yields a sanitised EPUB.
- Oversized image / decompression bomb is rejected within limits.
- Budget guard skips LLM calls once the cap is reached and the job still succeeds.

## 9.4 Ranking Evaluation

Offline dataset `tests/evals/ranking/` built from exported feedback (paper IDs + labels). CI job computes precision@10, nDCG@20 and coverage of exploration items, compares with the baseline stored on `main`, and fails on regression > 5 pp.

## 9.5 LLM Evaluation

- Dataset of 30–50 abstracts across fields with reference expectations.
- Automated checks per output: schema validity; length bounds; no claims absent from the abstract (LLM-as-judge with a fixed rubric, scored 1–5); readability (Flesch–Kincaid grade ≤ 12); no hallucinated numbers (numeric tokens must appear in the source).
- Run on every prompt or model change; results stored as CI artefacts; merge blocked if mean faithfulness score drops by > 0.3.


# 10. CI/CD

## 10.1 Branching and Release

- Trunk-based development on `main`; short-lived feature branches (git worktrees supported); squash merge.
- Conventional Commits; release-please generates changelog and SemVer tags.
- Images tagged with SemVer and Git SHA; never `latest` in deployment manifests.

## 10.2 Pipeline (GitHub Actions)

```
pull_request:
  ├─ lint        ruff check, ruff format --check, mypy --strict, hadolint, import-linter
  ├─ secrets     gitleaks
  ├─ sast        semgrep, bandit, sonarcloud (quality gate)
  ├─ sca         pip-audit, trivy fs
  ├─ test        unit + integration (testcontainers) + contract, coverage ≥ 90%
  ├─ conversion  golden tests (if paths changed)
  ├─ evals       ranking + LLM evals (if paths changed; uses budgeted key)
  └─ iac         terraform fmt/validate, checkov/trivy config, helm lint

push to main:
  ├─ (all of the above)
  ├─ build       docker buildx (app + converter), cache to GHA
  ├─ scan        trivy image (gate: no critical)
  ├─ sbom        syft → CycloneDX, attest
  ├─ sign        cosign keyless (OIDC)
  ├─ publish     GHCR
  ├─ deploy-stg  phase 1: compose pull/up via Tailscale-connected runner
  │              phase 2: bump image tag in GitOps repo → Argo CD sync (staging namespace)
  ├─ e2e         end-to-end suite against staging
  └─ dast        OWASP ZAP baseline + API scan against staging

tag v*:
  └─ promote     update production values (manual approval environment)
```

Workflow hardening: actions pinned by commit SHA; `permissions:` minimised per job (default `contents: read`); OIDC for cloud and registry; no secrets exposed to workflows triggered by forks.

Current state (M0): `.github/workflows/ci.yml` runs pre-commit (ruff format, ruff check, mypy), pytest with the coverage gate and the Sphinx build. The remaining jobs above are added by the milestone that introduces them.

## 10.3 Runners and Homelab Access

Deployment to the homelab uses either (a) a self-hosted runner on the M710q running as an unprivileged user with access limited to the deployment directory/namespace, or (b) GitOps pull (Argo CD) so that CI never needs inbound access to the homelab. Option (b) is the target architecture (ADR-008).


# 11. Deployment

## 11.1 Phase 1 — Docker Compose (Milestones M0–M3)

Services: `postgres` (pgvector image), `migrate` (one-shot Alembic), `api`, `worker`, `converter` (on an internal network with the worker only, no published port; 6.5.4), `mailpit` (staging only). Managed through Dockhand; health monitored by Uptime Kuma via `/readyz`. The web UI is bound to the host's Tailscale interface (or published through `tailscale serve` with HTTPS) and not to `0.0.0.0`.

## 11.2 Phase 2 — Kubernetes (k3s) with GitOps (Milestone M4+)

| Element | Choice |
|---|---|
| Distribution | k3s single node; Traefik ingress (bundled) restricted to tailnet; or `tailscale` operator for ingress |
| Packaging | Helm chart `deploy/helm/arx` with values per environment (`staging`, `prod` namespaces) |
| GitOps | Argo CD watching the `deploy/` path (or a separate GitOps repo); automated sync for staging, manual for prod |
| Database | PostgreSQL as StatefulSet with local-path PV (or CloudNativePG operator if resources allow) |
| Workloads | `api` Deployment; `worker` Deployment (replicas: 1, `strategy: Recreate`); `converter` Deployment (replicas: 1) with a ClusterIP Service, called only by the worker (6.5.4) |
| Jobs | Backups as Kubernetes CronJob calling `arx backup` |
| Policies | Kyverno (signed images, non-root, limits); NetworkPolicies: default deny, explicit egress for worker (arXiv, LLM, SMTP, object storage), converter: ingress from the worker only, no egress |
| Secrets | Sealed Secrets |
| Observability | kube-prometheus-stack (trimmed) or Prometheus + Grafana Helm charts with reduced retention |

## 11.3 Cloud (Terraform)

Scope kept minimal and cost-aware; provider selectable (AWS or Azure modules with identical interfaces).

| Resource | AWS | Azure |
|---|---|---|
| Backup storage | S3 bucket: versioning, SSE, Object Lock (governance), lifecycle 30/90 days | Storage account + container: versioning, immutability policy, lifecycle |
| Host identity for uploads | IAM user-less: IAM Roles Anywhere or a scoped access key in Sealed Secret (least privilege: `PutObject` only on prefix) | Managed identity not available on-prem → SAS token or service principal with Storage Blob Data Contributor on container |
| CI identity | IAM role trusted for GitHub OIDC (repo + branch conditions) | Federated credential on app registration |
| Remote state | S3 + DynamoDB lock / S3 native locking | Storage account backend |
| Budget | AWS Budgets alert | Cost Management budget alert |
| Optional | Off-site staging on a small VM / container service for DAST, destroyed after run | Same with Container Apps |

## 11.4 Host Configuration (Ansible)

Playbook `infra/ansible/site.yml`: OS hardening (unattended upgrades, SSH key-only, fail2ban), Docker/k3s installation, Tailscale, firewall (nftables: deny inbound except tailnet), node exporter, log rotation, backup key placement.

## 11.5 Backup and Restore

- Daily `pg_dump -Fc` → `age` encryption → upload to object storage under `backups/YYYY/MM/DD/`.
- Retention: 30 daily, 12 monthly.
- Monthly automated restore test into a temporary database, followed by integrity queries (row counts, latest library item) — result exported as metric.
- Restore runbook: stop worker → restore dump into new database → run migrations → switch connection string → start services → verify `/readyz` and library counts.


# 12. Configuration Reference

Variables are read from the environment or a local `.env`. Keys in `.env` without the `ARX_` prefix (e.g. Compose's `POSTGRES_*`) are ignored; an `ARX_*` key in `.env` that no implemented setting defines is rejected, so a misspelt name fails at start-up. Variables are implemented with the milestone that first needs them; until then their keys are rejected too (M0 implements the SMTP, delivery, arXiv and database variables).

| Variable | Default | Description |
|---|---|---|
| `ARX_ENV` | `dev` | `dev` / `staging` / `prod` |
| `ARX_DATABASE_URL_FILE` | `/run/secrets/database_url` | Secret: PostgreSQL URL `postgresql://user:password@host:port/db`; the psycopg 3 driver is always used. Needed only by commands that use the database and by Alembic |
| `ARX_TIMEZONE` | `Europe/Warsaw` | Scheduling timezone |
| `ARX_ARXIV_MIN_INTERVAL_S` | `3.0` | Minimum spacing between arXiv requests *(verify)* |
| `ARX_ARXIV_USER_AGENT` | `arx/<ver> (mailto:<ARX_DELIVERY_FROM>)` | Identifying User-Agent |
| `ARX_ARXIV_API_BASE` / `_RSS_BASE` / `_HTML_BASE` | arXiv defaults | Endpoint base URLs *(verify)* |
| `ARX_HARVEST_CRON` | `30 6 * * 1-5` | Daily harvest schedule (arXiv announces on weekdays) |
| `ARX_DIGEST_CRON` | `30 7 * * *` | Digest schedule (FR-DLV-04): daily by default, e.g. `30 7 * * 6` for weekly on Saturday |
| `ARX_DIGEST_RECIPIENT` | first address in `ARX_DELIVERY_ALLOWED_RECIPIENTS` | Kindle address of the scheduled digest; settings refuse to load if it is not on the allowlist |
| `ARX_FEED_SIZE` | `20` | Items in daily feed |
| `ARX_EXPLORATION_RATIO` | `0.10` | Share of exploration items |
| `ARX_EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | fastembed model |
| `ARX_LLM_MODEL` | provider-specific | LiteLLM model string |
| `ARX_LLM_MONTHLY_BUDGET_USD` | `5` | Hard cap |
| `ARX_LLM_API_KEY_FILE` | `/run/secrets/llm_api_key` | Secret |
| `ARX_SMTP_HOST` / `_PORT` / `_USERNAME` | `smtp.gmail.com` / `587` / — | SMTP submission (STARTTLS) |
| `ARX_SMTP_PASSWORD_FILE` | `/run/secrets/smtp_password` | Secret |
| `ARX_DELIVERY_FROM` | — | Approved sender address |
| `ARX_DELIVERY_ALLOWED_RECIPIENTS` | — | Comma-separated `@kindle.com` addresses |
| `ARX_DELIVERY_MAX_BYTES` | `20971520` | Raw attachment limit, 20 MiB with headroom under Gmail's 25 MB *(verify)* |
| `ARX_STORAGE_PATH` | `/data/files` | Conversion cache location |
| `ARX_STORAGE_QUOTA_GB` | `10` | Cache eviction threshold |
| `ARX_SESSION_SECRET_FILE` | `/run/secrets/session_secret` | Cookie signing key |
| `ARX_OWNER_PASSWORD_HASH_FILE` | `/run/secrets/owner_password_hash` | Argon2id hash |
| `ARX_BACKUP_BUCKET` / `_PROVIDER` | — | Backup destination |
| `ARX_BACKUP_AGE_RECIPIENT` | — | `age` public key |
| `ARX_OTEL_ENABLED` | `false` | Tracing |


# 13. Architecture Decision Records (Summary)

| ADR | Decision | Status | Rationale / Consequences |
|---|---|---|---|
| ADR-001 | Modular monolith with `api` and `worker` processes | Accepted | Single user, single node; lowest operational cost; boundaries enforced by import-linter allow later extraction. |
| ADR-002 | PostgreSQL-backed job queue (`SKIP LOCKED`) instead of Redis/Celery/RabbitMQ | Accepted | No extra service on an 8 GB host; transactional enqueue; full visibility via SQL. Trade-off: must implement retries, leases and scheduling in-house (deliberate learning objective). |
| ADR-003 | pgvector for vector search | Accepted | Corpus ≤ 10<sup>5</sup> vectors; HNSW in Postgres is sufficient; avoids a separate vector DB. |
| ADR-004 | fastembed + `bge-small-en-v1.5` on CPU | Accepted | ~130 MB model, no PyTorch, adequate quality for abstracts; model name stored per embedding to allow re-indexing. |
| ADR-005 | LiteLLM as LLM abstraction; hosted API by default, Ollama optional | Accepted | Provider independence, cost tracking; only public data leaves the host. |
| ADR-006 | Render maths to PNG (via MathJax→SVG→PNG) rather than MathML/SVG in EPUB | Rejected (Q-3) | Device test on the Paperwhite 11 Signature (firmware 5.19.2): an EPUB built with pandoc `--mathml` renders maths acceptably. Maths stays MathML (FR-CNV-02, 6.5.1 step 4); the converter image needs no MathJax or resvg. |
| ADR-007 | HTMX + server-rendered templates instead of SPA | Accepted | Minimal JS, single deployable, phone-friendly. |
| ADR-008 | GitOps pull-based deployment (Argo CD) for phase 2 | Accepted | No inbound access to homelab from CI; Git as source of truth; drift detection. |
| ADR-009 | Converter tools isolated in separate container without egress | Accepted | Main attack surface (parsing untrusted documents) is sandboxed. The worker calls the long-running converter over an internal HTTP API, the same in Compose and k3s (Q-8, 6.5.4). |
| ADR-010 | Python 3.14 as implementation language | Accepted | Workload is I/O- and rate-limit-bound; ecosystem for ML/LLM; aligns with owner's career goals. 3.14 is the newest version all planned dependencies ship wheels for. A future performance-critical component MAY be written in Go behind an interface. |

Full ADRs are maintained as OKF `Decision` concepts in `docs/knowledge/decisions/` (one file per ADR, e.g. `adr-001-modular-monolith.md`). This table is the summary; the concept file is authoritative when they differ.


# 14. Delivery Plan

Cadence assumption: ~3 evenings × 1.5 h + one longer weekend session per week. Each milestone ends with a tagged release and a demoable outcome.

| Milestone | Scope | Exit criteria (Definition of Done) | Est. |
|---|---|---|---|
| **M0 — Walking skeleton** | Repo, uv, ruff, mypy, pytest; Compose with Postgres+pgvector; Alembic; manual script: send one paper by arXiv ID or URL (`arx kindle`), then list the latest announced papers of one category (`arx today`); convert one HTML paper with pandoc, maths as MathML; e-mail to Kindle | A real paper, converted by Arx, is readable on the Kindle; CI runs lint + tests | 1 week |
| **M1 — Core pipeline** | Job queue + scheduler + rate limiter; harvest, probe, convert (HTML path with figures and tables; MathML maths since M0), deliver; epubcheck; delivery history; `arx search` over all of arXiv with *sent* / *stored* markers (FR-DSC-08, once `paper` exists); digest queue and scheduled digest EPUB (FR-DLV-04, FR-DLV-08, FR-CNV-07, after convert and deliver); minimal UI (feed list, send and queue buttons), reachable over the tailnet only, without login (Q-7) | Daily harvest runs unattended for 5 consecutive weekdays; 0 rate-limit violations; integration tests for queue semantics; a scheduled digest of queued papers is readable on the Kindle | 3–4 weeks |
| **M2 — Secure CI/CD** | Full PR pipeline (SAST, SCA, secrets, coverage gate), image build/scan/SBOM/sign, GHCR, automated deploy to homelab staging (Compose) | A PR with a planted secret or critical CVE is blocked; signed images deployed automatically | 1 week |
| **M3 — Discovery & library** | Full web UI (FR-UI-02) with owner login (FR-ADM-05, Q-7); embeddings, interests, ranker v1, feedback, explanations, library (statuses, tags, notes, keyword + semantic search), Search view over arXiv and the *library* marker (FR-DSC-08, FR-UI-02), LLM summaries with budget guard, ranking/LLM evals in CI | Daily feed is useful (owner's precision@10 ≥ 0.5 after 2 weeks of feedback); eval jobs gate PRs | 2–3 weeks |
| **M4 — Kubernetes & GitOps** | k3s via Ansible; Helm chart; Argo CD; Sealed Secrets; NetworkPolicies; Kyverno policies | Push to `main` → staging updated by Argo CD without manual steps; unsigned image rejected | 2 weeks |
| **M5 — Observability** | Metrics, dashboards, alerts, runbooks, push notifications | Simulated failure (stop SMTP) produces alert and runbook-guided recovery | 1 week |
| **M6 — Cloud & backups** | Terraform (AWS or Azure) for backup storage, OIDC for CI, budgets; backup CronJob; automated restore test | Successful restore from cloud backup within RTO | 1 week |
| **M7 — DAST & hardening** | OWASP ZAP in pipeline, threat model review, container hardening audit, performance tests | No high-risk ZAP findings; NFR-01..05 verified | 1 week |
| **M8 — Extras (P1/P2)** | PDF fallback, Kindle profiles, collections, BibTeX export, clippings import, RAG assistant (LangGraph) | Feature-specific acceptance tests pass | ongoing |

Implementation guidance for AI-assisted development: agents implement scoped changes, core mechanisms included, test-first (Section 9.1); the `mr-reviewer` agent reviews every merge request and the owner raises questions and adjustments. Each milestone SHOULD be broken into spec changes referencing the requirement IDs in this document.


# 15. Risks and Open Questions

## 15.1 Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-1 | arXiv HTML rendition missing or broken for a share of papers | Medium | Medium | PDF reflow fallback; quality flag in UI; golden tests on diverse papers |
| R-2 | Kindle rendering of maths/tables poorer than expected | Medium | High | Maths: MathML confirmed on the target device (Q-3); author macros texmath cannot parse fall back to TeX text, covered by the heavy-maths golden set; wide tables as images (FR-CNV-04); golden tests with heavy maths; profile tuning |
| R-3 | Changes to Send to Kindle (formats, limits, e-mail channel) | Low–Medium | High | Delivery adapter interface; alternative: download via UI / USB |
| R-4 | arXiv endpoint or policy changes | Low | Medium | Configurable endpoints; contract tests refreshed monthly |
| R-5 | Memory exhaustion on 8 GB host after adding k3s and monitoring | Medium | Medium | Resource budget (8.6); trimmed monitoring; phase 2 only after phase 1 measured |
| R-6 | LLM cost overrun | Low | Low | Hard budget guard; local Ollama option |
| R-7 | Scope creep stalls progress | Medium | High | Milestones with strict exit criteria; P2 features deferred |
| R-8 | Ranking quality insufficient with little feedback | Medium | Medium | Seed interests, exploration slots, quick feedback UI |
| R-9 | Native-extension dependencies lag new Python releases (onnxruntime had no 3.15 wheels at 0.2) | Medium | Medium | Pin Python to the newest version every dependency supports; upgrade only after checking wheels |

## 15.2 Open Questions

| ID | Question | Resolve by | Answer |
|---|---|---|---|
| Q-1 | Which Kindle model/resolution is the default profile? | M0 | Paperwhite Signature Edition (11th gen), 1236 × 1648 px, 300 dpi, greyscale (6.5) |
| Q-2 | Daily listing source: RSS per category vs. API date query — which is more complete and stable? | M1 (spike) | Open; M0 uses RSS (`arx today`, 6.6.1) as a stopgap |
| Q-3 | MathML vs. PNG maths: does the target Kindle render MathML from personal documents acceptably? | M1 (device test) | Yes: an EPUB built with pandoc `--mathml` renders maths acceptably on the Paperwhite 11 Signature, firmware 5.19.2; ADR-006 rejected (FR-CNV-02, 6.5.1) |
| Q-4 | Which SMTP provider will be used as the approved sender? | M0 | Dedicated Gmail account, app password, STARTTLS 587 (6.6.3) |
| Q-5 | AWS or Azure for backups and OIDC (both supported by the design)? | M6 | Open |
| Q-6 | Is CloudNativePG affordable in memory vs. a plain StatefulSet? | M4 | Open |
| Q-7 | Authentication: T1 requires an owner login (Argon2id, session cookie, CSRF), but no FR, endpoint or milestone covers it. Is tailnet-only access enough until a given milestone, and which milestone adds login? | M1 | Tailnet-only, no login, for M1's minimal UI; owner login (FR-ADM-05) arrives in M3 with the full UI (7.2 T1, 14) |
| Q-8 | Converter interface: containers in one pod cannot run each other's binaries as subprocesses (6.5.4). Choose HTTP sidecar vs. a job-scoped container per conversion, for both Compose and k3s. | M1 | Long-running HTTP service (own Deployment in k3s): the converter serves a narrow internal HTTP API to the worker, the same in Compose and k3s (6.5.4, 11.1, 11.2) |
| Q-9 | Ranker v1: `novelty_bonus` is undefined, and the exploration rule "min. 1 when *N* ≥ 10" reuses *N* (negative history) — feed size meant? | M3 | Open |
| Q-10 | The ranking evaluation dataset (9.4) is built from the owner's feedback. May it be committed to the repository, or must it stay private (CI artefact / private bucket)? | M3 | Open |
| Q-11 | Database driver: spec says asyncpg; the repository already depends on psycopg 3, which also works async with SQLAlchemy and sync for Alembic/CLI. Pick one. | M0 | psycopg 3 (5.5) |
| Q-12 | FR-ENR-04 requires token usage and cost per LLM output, but `paper_summary` has no link to `llm_usage`. Add a foreign key or columns? | M3 | Open |
| Q-13 | Logging: structlog (8.1) vs. the project rule `logging.getLogger(__name__)`. Proposed: stdlib loggers in modules, structlog only as the JSON formatter configured in the entry point. | M1 | Accepted as proposed (5.5, 8.1) |
| Q-14 | Minor inconsistencies to fix when implementing: `probe_html` dedup key uses `<ver>` but the payload has no version; FR-CNV-09 cache key omits `kind` while the DDL index includes it; FR-DSC-03 says *save* while the `feedback.signal` check says `saved`; the component view (5.2) puts `rate_limiter` under `jobs/`, while 6.1 and Appendix A put it under `adapters/arxiv/`. | M1 | Fixed in 5.2, 6.3.4, FR-CNV-09, FR-DSC-03; rate limiter in `adapters/arxiv/` |


# Appendix A. Requirement Traceability Template

| Requirement | Design section | Test(s) | Milestone |
|---|---|---|---|
| FR-ING-02 | 5.3, 6.3.4, 6.6.1 | `tests/domain/test_announcement.py`, `tests/adapters/arxiv/test_client.py` (`contract`), `tests/services/test_listing.py`, `tests/cli/test_main.py` (M0); `tests/jobs/handlers/test_harvest.py::test_daily_harvest_idempotent` (`integration`) | M0 (partial: one category, manual), M1 (all subscribed, scheduled) |
| FR-ING-03 | 6.2.2, 6.3.4 | `tests/adapters/db/test_paper_repository.py` (`integration`); `…::test_reharvest_no_duplicates` (`integration`) | M0 (partial: idempotent paper upsert), M1 (harvest) |
| FR-ING-04 | 6.6.1 | `tests/domain/test_arxiv_id.py`, `tests/adapters/arxiv/test_client.py` (`contract`), `tests/services/test_kindle.py`, `tests/cli/test_main.py` | M0 (ID and URL, HTML path), M1 (stored) |
| FR-ING-07 | 6.2.2 | `tests/adapters/db/test_paper_repository.py::test_storing_the_same_paper_again_keeps_one_row` (`integration`) | M0 (partial: one row per arXiv ID), M1 (harvest of cross-lists) |
| FR-CNV-01 | 6.5.1 | `tests/services/test_conversion.py`, `tests/adapters/conversion/test_html_cleaner.py`, `tests/adapters/conversion/test_epub_builder.py`; golden set (`golden`) in M1 | M0 (partial: text, TOC, title page), M1 (full) |
| FR-CNV-02 | 6.5.1 steps 4 and 9 | `tests/adapters/conversion/test_html_cleaner.py`, `tests/adapters/conversion/test_epub_builder.py`; golden set with heavy maths (`golden`) in M1 | M0 (MathML), M1 (golden set) |
| FR-CNV-07 | 6.5.3 | `tests/adapters/conversion/test_epub_builder.py`, golden digest (`golden`) | M1 |
| FR-CNV-08 | 6.5.1 step 10 | `tests/adapters/conversion/test_epubcheck.py` | M1 |
| FR-ADM-05 | 7.2 T1, 12 | `tests/web/test_auth.py` | M3 |
| FR-DLV-01 | 6.6.1 | `tests/services/test_kindle.py`, `tests/cli/test_main.py` | M0 (CLI), M1 (UI) |
| FR-DLV-02 | 6.6.3 | `tests/services/test_delivery.py`, `tests/adapters/mail/test_smtp_mailer.py`, `tests/test_settings.py`, `tests/test_bootstrap.py`, `tests/cli/test_main.py` | M0 |
| FR-DLV-03 | 6.6.3 | `tests/services/test_delivery.py`, `tests/test_settings.py`, `tests/test_bootstrap.py` | M0 (partial: reject), M1 (downscale option) |
| FR-DLV-04 | 5.3, 6.3.4, 6.5.3, 12 | `tests/jobs/handlers/test_digest.py` (`integration`) | M1 |
| FR-DLV-06 | 6.3.3, 6.6.3 | `tests/jobs/handlers/test_deliver.py` (`integration`) | M1 |
| FR-DLV-07 | 6.6.3, 7.2 T9 | `tests/services/test_delivery.py`, `tests/services/test_kindle.py`, `tests/test_settings.py`, `tests/cli/test_main.py` | M0 (allowlist), M1 (T9 rate limit) |
| FR-DLV-08 | 6.2.2, 6.5.3, 6.7 | `tests/services/test_digest_queue.py`, `tests/jobs/handlers/test_digest.py` (`integration`), `tests/jobs/test_queue.py::test_dead_digest_job_fails_delivery_and_releases_items` (`integration`), `tests/cli/test_main.py` | M1 (CLI, feed button), M3 (Search and Library views) |
| FR-DSC-02 | 6.4 | `tests/domain/test_ranking.py`, `tests/evals/ranking` | M3 |
| FR-DSC-08 | 6.6.1, 6.7, 6.8 | `tests/adapters/arxiv/test_client.py` (`contract`), `tests/services/test_search.py`, `tests/cli/test_main.py` | M1 (CLI, *sent* / *stored*), M3 (Search view, *library*) |
| NFR-16 | 6.6.1 | `tests/adapters/arxiv/test_client.py::test_requests_are_spaced_by_the_minimum_interval`, `…::test_feed_requests_are_spaced_like_the_others`, `tests/test_settings.py` (M0 wait); `tests/adapters/arxiv/test_rate_limiter.py` (property); `tests/adapters/arxiv/test_rate_limiter_lock.py` (`integration`: CLI search beside a worker) | M0 (partial: fixed wait), M1 (limiter) |
| … | … | … | … |

The full matrix is generated by CI from `@pytest.mark.req` markers.

# Appendix B. Example arXiv Categories

| Code | Field |
|---|---|
| `cs.LG`, `cs.AI`, `cs.CL` | Machine learning, AI, computation and language |
| `cs.CR`, `cs.DC` | Cryptography and security; distributed computing |
| `astro-ph.HE`, `astro-ph.EP` | High-energy astrophysics; earth and planetary astrophysics |
| `physics.plasm-ph` | Plasma physics (incl. fusion) |
| `q-bio.NC` | Neurons and cognition |
| `cond-mat.mtrl-sci` | Materials science |
| `econ.GN`, `q-fin.ST` | General economics; statistical finance |

Category list SHOULD be loaded from arXiv's taxonomy at setup rather than hard-coded.

# Appendix C. References

- arXiv API Terms of Use — <https://info.arxiv.org/help/api/tou.html>
- arXiv: HTML as an accessible format for papers — <https://info.arxiv.org/about/accessible_HTML.html>
- arXiv blog: "Accessibility update: arXiv now offers papers in HTML format" (Dec 2023) — <https://blog.arxiv.org/2023/12/21/accessibility-update-arxiv-now-offers-papers-in-html-format>
- RFC 2119 (requirement levels), RFC 9457 (Problem Details for HTTP APIs)
- OWASP ASVS 4.x; OWASP Top 10; SLSA framework; CycloneDX specification
- PostgreSQL documentation: `SELECT … FOR UPDATE SKIP LOCKED`, `LISTEN/NOTIFY`, advisory locks
- pgvector, fastembed, LiteLLM, pandoc, epubcheck, k2pdfopt project documentation
