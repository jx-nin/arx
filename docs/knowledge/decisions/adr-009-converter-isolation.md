---
type: Decision
title: "ADR-009 Isolated converter"
description: pandoc, MathJax, k2pdfopt and epubcheck run in a separate container with no network or DB credentials.
tags: [security, conversion, adr]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-10-30T00:00:00Z }
---

# Decision

* Parsing untrusted documents is the main attack surface, so it runs in a sandbox.
* The interface between worker and converter is still open (spec Q-8).

Summary row: [specification](/specs/tds.md), section 13.
