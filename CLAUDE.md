# Project rules

## Workflow
- Small commits, one logical change each.
- Split work into slices that each fit one merge request; one branch per slice off `main`.
- Before opening or merging an MR, run the `mr-reviewer` agent (fresh context, Opus 5.5, medium effort) and resolve its blocking findings.
- Every slice that adds a concept, decision or component updates the knowledge graph (see below).

## Spec
- `docs/spec/tds.md` is the authoritative spec; for decisions the ADR concepts in `docs/knowledge/decisions/` win. Requirement IDs (`FR-*`, `NFR-*`) go in `@pytest.mark.req("…")`; those plus `ADR-*` and `Q-*` go in commit messages and MR descriptions.
- A change that alters specified behaviour updates the spec in the same MR and adds a revision-history row.
- Don't start a slice whose milestone has open questions (spec 15.2) that it depends on; ask first.
- Agents implement all code, core mechanisms included (job queue, rate limiter, ranking, conversion pipeline). Review is agentic (`mr-reviewer`); the owner raises questions and adjustments.
- Layering (spec 5.2): `domain` imports nothing else; services depend on adapter `Protocol`s; concrete adapters are wired only in `bootstrap.py`; `web`/`api`/`cli` depend only on services.

## Code
- Readable over clever: prefer the clearer version even when it is longer.
- Keep files under 500 lines; split by responsibility before reaching that.
- Layout per PEP 8: module docstring, then imports (stdlib, third-party, local; enforced by ruff `I`), then constants, then code.
- Full type hints everywhere; `mypy --strict` must pass.
- Docstrings in Sphinx reST style (`:param x:`, `:returns:`, `:raises:`) on every public module, class and function.
- Logging: `logger = logging.getLogger(__name__)` per module; configure handlers only in the entry point. `print` only for CLI output meant for the user.

## Tests
- `pytest` under `tests/`, mirroring the `src/arx/` layout; test level via markers (`integration`, `contract`, `golden`), unmarked = unit. Fixtures in `tests/fixtures/`, eval datasets in `tests/evals/`.
- Coverage must stay at or above 90% (`fail_under` in `pyproject.toml`); aim higher.
- Test-first per spec 9.1: every behaviour change in any layer starts with a failing test; a bug fix's first test reproduces the bug. Exceptions are listed there.
- TDD steps are working practice, not history: commit a behaviour with its tests once green, and never name red/green/refactor in commits or MRs.

## Tooling
- Install hooks once: `uv run pre-commit install`.
- All checks: `uv run pre-commit run --all-files` (ruff format, ruff check, mypy --strict).
- CI (`.github/workflows/ci.yml`) runs the same checks plus tests and docs.
- Tests: `uv run pytest`. Docs: `uv run sphinx-build docs docs/_build`.

## Knowledge graph (OKF v0.2)
- Bundle lives in `docs/knowledge/`; spec: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
- One concept per `.md` file with YAML frontmatter; `type` is required, add `title`, `description`, `tags`.
- Link concepts with bundle-absolute markdown links, e.g. `[tooling](/decisions/tooling.md)`.
- `index.md` lists concepts; `log.md` gets a dated entry (`## YYYY-MM-DD`, newest first) per change.
- `index.md` and `log.md` are reserved names, never use them for concepts.
