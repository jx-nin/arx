---
type: Decision
title: Test layout
description: Tests mirror src/arx/; the test level comes from pytest markers, not folders.
tags: [testing, tooling]
status: stable
generated: { by: "agent:claude-opus-5-5", at: 2026-10-30T00:00:00Z }
---

# Decision

* `tests/` mirrors `src/arx/`, as required by `CLAUDE.md`. This replaces the `tests/unit|integration|…` folders in the spec draft.
* Unmarked tests are unit tests. `integration`, `contract` and `golden` mark the other levels, and `req("FR-…")` links a test to a requirement in the [specification](/specs/tds.md).
* Markers are registered in `pyproject.toml` and `--strict-markers` rejects typos.
* `tests/fixtures/` holds recorded inputs and `tests/evals/` holds evaluation datasets.
