# arx

Fetch and read arXiv papers.

Design and requirements: [docs/spec/tds.md](docs/spec/tds.md). Decisions: [docs/knowledge/](docs/knowledge/index.md).

Requires Python 3.14 (pinned in `.python-version`) and [pandoc](https://pandoc.org/installing.html) 3.7 on `PATH` (CI pins 3.7.0.2) for EPUB conversion.

## Setup

```bash
uv sync
uv run pre-commit install
docker compose up -d   # local Postgres with pgvector
```

Settings are read from `ARX_*` environment variables or a local `.env` file (not committed); see spec section 12. Secrets never go in `.env`: the SMTP app password lives in the file named by `ARX_SMTP_PASSWORD_FILE`.

## Send an EPUB to the Kindle

```bash
uv run arx send paper.epub --to you@kindle.com --id 2401.01234v2 \
  --title "Paper title" --author "First Author" --published 2024-01-03
```

`--to` must be in `ARX_DELIVERY_ALLOWED_RECIPIENTS`; the sender `ARX_DELIVERY_FROM` must be on Amazon's approved list.

## Development

```bash
uv run pre-commit run --all-files   # ruff format, ruff check, mypy --strict
uv run pytest
uv run sphinx-build docs docs/_build
```
