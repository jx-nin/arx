# arx

Fetch and read arXiv papers.

Design and requirements: [docs/spec/tds.md](docs/spec/tds.md). Decisions: [docs/knowledge/](docs/knowledge/index.md).

Requires Python 3.14 (pinned in `.python-version`).

## Setup

```bash
uv sync
uv run pre-commit install
docker compose up -d   # local Postgres with pgvector
```

Settings are read from a local `.env` file (not committed).

## Development

```bash
uv run pre-commit run --all-files   # ruff format, ruff check, mypy --strict
uv run pytest
uv run sphinx-build docs docs/_build
```
