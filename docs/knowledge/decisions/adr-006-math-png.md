---
type: Decision
title: "ADR-006 Maths rendered to PNG (rejected)"
description: Rejected after the device test; maths goes into the EPUB as MathML written by pandoc --mathml.
tags: [conversion, kindle, adr]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-11-03T00:00:00Z }
---

# Decision

* Rejected (spec Q-3). The proposal was MathJax to SVG to PNG, because Kindle support for MathML in personal documents seemed inconsistent.
* Device test: the owner sent an EPUB built with pandoc `--mathml` to the Paperwhite 11 Signature (firmware 5.19.2, [default Kindle profile](/decisions/kindle-profile.md)); the maths renders acceptably.
* New decision: keep LaTeXML's MathML and let pandoc `--mathml` write it into the EPUB, TeX kept as annotation and `alttext` (FR-CNV-02, spec 6.5.1 steps 4 and 9). Expressions pandoc cannot convert stay as TeX text with a logged warning.
* Consequences: no MathJax, Node.js or resvg in the [converter](/decisions/adr-009-converter-isolation.md); maths scales with the font. Wide tables are still rendered as images (FR-CNV-04).

Summary row: [specification](/specs/tds.md), section 13. Implemented in [EPUB conversion](/components/epub-conversion.md).
