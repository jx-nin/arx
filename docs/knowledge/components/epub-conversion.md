---
type: Component
title: EPUB conversion
description: M0 path from an arXiv HTML rendition to an EPUB 3 file styled for the Kindle, built with pandoc.
tags: [conversion, kindle]
status: draft
generated: { by: "agent:claude-opus-5-5", at: 2026-10-31T00:00:00Z }
---

# Component

* Covers FR-CNV-01 for M0 (spec 6.5.1 steps 3, 8 and 9); heading normalisation (step 3), maths, figures, tables, sanitising and epubcheck follow in M1.
* `services/conversion.py`: `ConversionService.convert_html` puts a title page in front of the cleaned article; it depends on the `HtmlCleaner` and `EpubBuilder` protocols.
* `adapters/conversion/html_cleaner.py`: `LatexmlHtmlCleaner` keeps `<article>` (lxml), dropping arXiv chrome and the LaTeXML title, authors and abstract the title page repeats.
* `adapters/conversion/epub_builder.py`: `PandocEpubBuilder` runs pandoc 3.7 (`--to=epub3 --toc --toc-depth=2 --epub-title-page=false`, language `en`) in a temporary working directory, with package metadata from the paper; pandoc warnings are logged.
* `adapters/conversion/kindle.css`: stylesheet for the [default Kindle profile](/decisions/kindle-profile.md), relative sizes only; tuned on the device.
* Shortcut: pandoc still embeds absolute paths from `img src` and fetches remote URLs over the network, until sanitising (step 2) and [ADR-009](/decisions/adr-009-converter-isolation.md) isolation land.
* Known limit: pandoc reads `--metadata` values as YAML scalars, so a title or author of `True` becomes `true` in the package metadata.
* pandoc runs as a local subprocess until the converter interface (spec Q-8) is decided.
