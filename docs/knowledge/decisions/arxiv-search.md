---
type: Decision
title: Keyword search of all of arXiv
description: The owner searches all of arXiv by keyword, and each result shows whether the paper is already in Arx.
tags: [arxiv, discovery, search]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-11-03T00:00:00Z }  # decided by human:jx-nin
---

# Decision

* Owner decision, recorded as FR-DSC-08 (P0) in the [specification](/specs/tds.md) (v0.10, sections 6.6.1, 6.7, 6.8).
* Searches all of arXiv through the API `search_query`, not only stored papers, which is what library search (FR-LIB-04) covers.
* Each result carries a marker: *sent* and *library* (both if both apply), otherwise *stored*. A result without a marker is new to Arx. Results are not stored.
* Order: CLI `arx search` in M1 once the `paper` table exists, then the UI Search view (FR-UI-02) in M3.
* Every search page is one request through the [arXiv rate limiter](/decisions/arxiv-rate-limiter.md), advisory lock included, so a CLI search can't break NFR-16 beside a worker.
* Saved searches that run with the harvest (FR-ING-08) stay P2 and build on this.
