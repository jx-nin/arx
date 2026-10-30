# Project rules

## Workflow
- Small commits, one logical change each.
- Split work into slices that each fit one merge request; one branch per slice off `main`.
- Before opening or merging an MR, run the `mr-reviewer` agent (fresh context, Opus 5.5, medium effort) and resolve its blocking findings.
- Every slice that adds a concept, decision or component updates the knowledge graph (see below).

## Code
- Readable over clever: prefer the clearer version even when it is longer.
- Keep files under 500 lines; split by responsibility before reaching that.
- Layout per PEP 8: module docstring, then imports (stdlib, third-party, local; enforced by ruff `I`), then constants, then code.
- Full type hints everywhere; `mypy --strict` must pass.
- Docstrings in Sphinx reST style (`:param x:`, `:returns:`, `:raises:`) on every public module, class and function.
- Logging: `logger = logging.getLogger(__name__)` per module; configure handlers only in the entry point. `print` only for CLI output meant for the user.

## Tests
- `pytest` under `tests/`, mirroring the `src/arx/` layout.
- Coverage must stay at or above 90% (`fail_under` in `pyproject.toml`); aim higher.

## Tooling
- Install hooks once: `uv run pre-commit install`.
- All checks: `uv run pre-commit run --all-files` (ruff format, ruff check, mypy --strict).
- Tests: `uv run pytest`. Docs: `uv run sphinx-build docs docs/_build`.

## Knowledge graph (OKF v0.2)
- Bundle lives in `docs/knowledge/`; spec: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
- One concept per `.md` file with YAML frontmatter; `type` is required, add `title`, `description`, `tags`.
- Link concepts with bundle-absolute markdown links, e.g. `[tooling](/decisions/tooling.md)`.
- `index.md` lists concepts; `log.md` gets a dated entry (`## YYYY-MM-DD`, newest first) per change.
- `index.md` and `log.md` are reserved names, never use them for concepts.
