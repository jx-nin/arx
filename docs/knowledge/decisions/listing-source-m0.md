---
type: Decision
title: RSS as the M0 daily listing source
description: M0 lists a category's announced papers from arXiv RSS; Q-2 (RSS vs. API date query) stays open for the M1 spike.
tags: [arxiv, ingestion]
status: draft
generated: { by: "agent:claude-opus-5-5", at: 2026-11-03T00:00:00Z }  # decided by human:jx-nin
---

# Decision

* Stopgap for Q-2 of the [specification](/specs/tds.md) (v0.10): [`arx today`](/components/daily-listing.md) reads `rss.arxiv.org/rss/<category>`; Q-2 stays open and the M1 spike still compares RSS with the API query by `submittedDate`.
* RSS gives exactly one day's announcement with its announce type (new, cross, replace, replace-cross) in one request, which is all a manual M0 listing needs.
* Trade-off: RSS has no history, so a missed day cannot be fetched later; that matters only for the scheduled harvest (FR-ING-02, M1).
