---
type: Decision
title: "ADR-009 Isolated converter"
description: pandoc, k2pdfopt and epubcheck run in a separate container with no network or DB credentials.
tags: [security, conversion, adr]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-11-03T00:00:00Z }
---

# Decision

* Parsing untrusted documents is the main attack surface, so it runs in a sandbox.
* Interface (spec Q-8): the converter is a long-running container serving a narrow internal HTTP API; the worker is its only client and sends inputs and receives outputs in the request and response, with no shared volume.
* The same image and API in both phases: a Compose service on an internal network with the worker only; in k3s its own Deployment and ClusterIP Service, so a NetworkPolicy can deny its egress while the worker keeps its own (spec 6.5.4, 11.2).
* M0 still runs pandoc as a local subprocess (see [EPUB conversion](/components/epub-conversion.md)).

Summary row: [specification](/specs/tds.md), section 13.
