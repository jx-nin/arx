---
type: Decision
title: Merge request review
description: Every merge request is reviewed by the mr-reviewer agent in a fresh context.
tags: [process, review]
status: stable
generated: { by: human:jx-nin, at: 2026-10-30T00:00:00Z }
---

# Decision

* The `mr-reviewer` agent (`.claude/agents/mr-reviewer.md`) runs on Opus 5.5 at medium effort with no prior context.
* It reviews only the branch diff against `main` and checks correctness, the rules in `CLAUDE.md`, style, structure, and that docs and this bundle stay in sync.
* It runs the same checks as the [tooling stack](/decisions/tooling.md) and never edits files.
* It flags changed behaviour that ships without tests, per [test-driven development](/decisions/tdd.md).
* Review is agentic: agents write all code, core mechanisms included; the owner raises questions and adjustments (spec v0.5, 9.1).
