---
type: Decision
title: Maths as MathML
description: pandoc --mathml writes maths into the EPUB as MathML, TeX kept as annotation; replaces ADR-006.
tags: [conversion, kindle]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-11-03T00:00:00Z }  # decided by human:jx-nin
---

# Decision

* Answers Q-3 of the [specification](/specs/tds.md) (v0.13; FR-CNV-02, 6.5.1 steps 4 and 9) and rejects [ADR-006](/decisions/adr-006-math-png.md).
* Device test: the owner sent an EPUB built with pandoc `--mathml` to the Paperwhite 11 Signature (firmware 5.19.2, [default Kindle profile](/decisions/kindle-profile.md)); the maths renders acceptably.
* pandoc ignores LaTeXML's MathML body and regenerates MathML from the `application/x-tex` annotation with texmath; the TeX stays as annotation.
* Limit: author macros texmath cannot parse stay as TeX text with a logged warning; the heavy-maths golden set (M1) watches this.
* Consequences: no MathJax, Node.js or resvg in the [converter](/decisions/adr-009-converter-isolation.md); maths scales with the font; the M1 nh3 allowlist must keep MathML. Wide tables are still rendered as images (FR-CNV-04).
* Implemented in [EPUB conversion](/components/epub-conversion.md).
