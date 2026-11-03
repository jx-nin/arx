---
type: Component
title: Daily listing of one category
description: M0 command `arx today CATEGORY` that lists the latest announced new papers and cross-lists of one arXiv category from RSS.
tags: [arxiv, ingestion]
status: draft
generated: { by: "agent:claude-opus-5-5", at: 2026-11-03T00:00:00Z }
---

# Component

* Covers FR-ING-02 partially for M0 (spec 6.6.1): one category, run by hand, nothing stored; the scheduled harvest of all subscribed categories follows in M1. Source per [RSS as the M0 daily listing source](/decisions/listing-source-m0.md).
* `domain/announcement.py`: `Announcement` (ID, version, title, authors, announce type) and `check_category`, which accepts only archive or `archive.subject` codes so nothing else reaches the URL path.
* `adapters/arxiv/client.py`: `ArxivClient.announcements` fetches the feed through the same spaced request path as the [arXiv client](/components/arxiv-client.md) and parses it with the same safe lxml parser; the versioned ID comes from the `oai:arXiv.org:<id>v<n>` guid, affiliations in parentheses are dropped from `dc:creator`. 404 raises `ValueError`; arXiv answers an unknown category with 400, which raises `OSError`.
* `services/listing.py`: `ListingService.today` checks the category before any request and keeps `new` and `cross` items; replacements are left out.
* `cli/main.py`: `arx today CATEGORY` prints `<id>v<n>  [cross] <title> — <first author>`; an empty feed (weekends, holidays) prints a one-line note with status 0, errors exit with status 1 and one line.
* feedparser is a dependency but ships no type hints, so the RSS is parsed with lxml like the API Atom.
