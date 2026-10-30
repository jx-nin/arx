---
type: Decision
title: Test-driven development
description: Every behaviour change is built test-first, with named exceptions; the history only shows finished behaviours.
tags: [process, testing]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-10-30T00:00:00Z }
---

# Decision

* Rule source: section 9.1 of the [specification](/specs/tds.md) (v0.3).
* Every behaviour change in any layer starts with a failing test; a bug fix's first test reproduces the bug. Tests follow the [test layout](/decisions/test-layout.md).
* Exceptions: trivial changes (renames, docs, config values that don't change specified behaviour); template markup, whose route or handler stays test-first; migrations, covered by integration tests written afterwards.
* Core mechanisms (job queue, rate limiter, ranking, conversion pipeline): agents write the failing tests from requirement IDs, the owner writes the code.
* Red, green and refactor are not separate commits: a commit holds one behaviour with its tests, all checks green, and MRs never name the phases.
* The [merge request review](/decisions/review.md) flags changed behaviour without tests.
