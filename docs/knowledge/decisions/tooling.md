---
type: Decision
title: Tooling stack
description: Formatter, linter, type checker, tests and docs tooling for the project.
tags: [tooling, quality]
status: stable
generated: { by: human:jx-nin, at: 2026-10-30T00:00:00Z }
---

# Decision

* `ruff format` (Black-compatible) and `ruff check` replace Black and flake8: one tool, already installed.
* `mypy --strict` is the only type checker; pyright was removed so two checkers cannot disagree.
* `pytest` with `pytest-cov`, coverage must stay at or above 90%.
* Sphinx `autodoc` builds API docs from reST docstrings.
* All checks run through `pre-commit` using the uv-locked versions.
