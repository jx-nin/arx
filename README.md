# arx

Fetch and read arXiv papers.

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
