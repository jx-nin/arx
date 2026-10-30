---
type: Decision
title: "ADR-006 Maths rendered to PNG"
description: Maths is rendered MathJax to SVG to PNG rather than embedded as MathML or SVG.
tags: [conversion, kindle, adr]
status: draft
generated: { by: "agent:claude-opus-5-5", at: 2026-10-30T00:00:00Z }
---

# Decision

* Proposed: Kindle support for MathML and SVG in personal documents is inconsistent, and PNG always displays.
* Trade-off: larger files and maths that doesn't scale, offset by the profile DPI.
* Still to check on the target device (spec Q-3) before this is accepted.

Summary row: [specification](/specs/tds.md), section 13.
