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

Settings are read from `ARX_*` environment variables or a local `.env` file (not committed); see spec section 12. Secrets never go in `.env`: the SMTP app password lives in the file named by `ARX_SMTP_PASSWORD_FILE`, the database URL in the file named by `ARX_DATABASE_URL_FILE`.

## Database migrations

```bash
docker compose up -d
mkdir -p ~/.config/arx
printf 'postgresql://arxiv:arxiv@127.0.0.1:5432/arxiv\n' > ~/.config/arx/database_url
export ARX_DATABASE_URL_FILE=~/.config/arx/database_url   # or set it in .env
uv run alembic upgrade head
```

Migrations live in `migrations/`; `arx send` and `arx kindle` do not use the database yet.

## Send a paper to the Kindle

```bash
uv run arx kindle https://arxiv.org/abs/2401.01234 --to you@kindle.com
```

Takes an arXiv ID (`2401.01234`, `2401.01234v2`) or an `arxiv.org/abs|pdf|html` URL, fetches the HTML version, converts it to EPUB and mails it. Papers without an HTML version are not supported yet.

## List today's papers of a category

```bash
uv run arx today cs.LG
```

Prints the latest announced new papers and cross-lists (`[cross]`) of one arXiv category, one line each: versioned ID, title, first author. Replacements of older papers are left out. Pass an ID from the list to `arx kindle`. On weekends and holidays arXiv announces nothing and the command says so. It reads the same settings as `arx kindle`, since the `User-Agent` names the sender address as contact.

## Send an EPUB to the Kindle

```bash
uv run arx send paper.epub --to you@kindle.com --id 2401.01234v2 \
  --title "Paper title" --author "First Author" --published 2024-01-03
```

`--to` must be in `ARX_DELIVERY_ALLOWED_RECIPIENTS`; the sender `ARX_DELIVERY_FROM` must be on Amazon's approved list.

## Development

```bash
uv run pre-commit run --all-files   # ruff format, ruff check, mypy --strict
uv run pytest                       # integration tests need Docker (testcontainers; WSL: enable Docker Desktop's WSL integration)
uv run sphinx-build docs docs/_build
```
