---
type: Decision
title: "ADR-006 Maths rendered to PNG (rejected)"
description: Rejected after the device test (Q-3); replaced by maths as MathML via pandoc.
tags: [conversion, kindle, adr]
status: deprecated
generated: { by: "agent:claude-opus-5-5", at: 2026-11-03T00:00:00Z }  # decided by human:jx-nin
---

# Decision

* Rejected (spec Q-3). The proposal was MathJax to SVG to PNG, because Kindle support for MathML in personal documents seemed inconsistent.
* The owner's device test showed MathML renders acceptably; see [maths as MathML](/decisions/maths-mathml.md).

Summary row: [specification](/specs/tds.md), section 13.
