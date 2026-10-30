---
type: Decision
title: "ADR-005 LiteLLM gateway"
description: All LLM calls go through LiteLLM; hosted API by default, local Ollama optional.
tags: [ml, llm, adr]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-10-30T00:00:00Z }
---

# Decision

* Provider independence and built-in cost tracking for the monthly budget guard.
* Only public data (title, abstract, headings) leaves the host.

Summary row: [specification](/specs/tds.md), section 13.
