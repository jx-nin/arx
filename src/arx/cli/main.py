"""The ``arx`` command; its entry point configures logging (spec 8.1)."""

import argparse
import logging
import sys
from collections.abc import Sequence
from datetime import UTC, date, datetime, time
from pathlib import Path

from pydantic import ValidationError

from arx.bootstrap import (
    build_delivery_service,
    build_kindle_service,
    build_listing_service,
)
from arx.domain.arxiv_id import VERSIONED_ID
from arx.domain.paper import Paper
from arx.settings import Settings


def main(argv: Sequence[str] | None = None) -> None:
    """Run the ``arx`` command.

    :param argv: Arguments without the program name; ``None`` reads
        ``sys.argv``.
    :raises SystemExit: On invalid arguments, an unknown paper, category or
        one without HTML rendition, a rejected delivery, invalid settings or a
        failed file, arXiv or SMTP operation, with the reason.
    """
    args = _parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        args.run(args)
    except ValidationError as error:
        # One line, and no input values: they may echo configured settings.
        fields = "; ".join(f"{_field(e['loc'])}: {e['msg']}" for e in error.errors())
        sys.exit(f"arx: invalid settings: {fields}")
    # Rejections are ValueErrors; arXiv and smtplib errors are OSErrors.
    except (ValueError, OSError) as error:
        sys.exit(f"arx: {error}")


def _parser() -> argparse.ArgumentParser:
    """Build the argument parser.

    :returns: Parser for the ``kindle``, ``today`` and ``send`` commands.
    """
    parser = argparse.ArgumentParser(
        prog="arx", description="Fetch and read arXiv papers."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    kindle = commands.add_parser(
        "kindle", help="fetch, convert and e-mail a paper to a Kindle (FR-ING-04)"
    )
    kindle.add_argument("paper", help="arXiv ID or abs, pdf or html URL")
    kindle.add_argument("--to", required=True, help="allowlisted Kindle address")
    kindle.set_defaults(run=_kindle)
    today = commands.add_parser(
        "today", help="list a category's latest announced papers (FR-ING-02)"
    )
    today.add_argument("category", help="arXiv category, e.g. cs.LG")
    today.set_defaults(run=_today)
    send = commands.add_parser("send", help="e-mail an EPUB to a Kindle (FR-DLV-02)")
    send.set_defaults(run=_send)
    send.add_argument("epub", type=Path, help="EPUB file to send")
    send.add_argument("--to", required=True, help="allowlisted Kindle address")
    send.add_argument(
        "--id",
        required=True,
        type=_versioned_id,
        help="versioned arXiv ID, e.g. 2401.01234v2",
    )
    send.add_argument("--title", required=True, help="paper title")
    send.add_argument(
        "--author",
        action="append",
        default=[],
        help="author name, repeated in listing order",
    )
    send.add_argument(
        "--published",
        required=True,
        type=_iso_date,
        help="date the first version was published, YYYY-MM-DD",
    )
    return parser


def _kindle(args: argparse.Namespace) -> None:
    """Fetch, convert and mail the paper the ``kindle`` arguments name.

    :param args: Parsed ``kindle`` arguments.
    :raises ValueError: If settings are invalid, the paper is unknown or has no
        HTML rendition, or delivery rejects the mail.
    :raises OSError: If an arXiv request or sending fails.
    """
    service = build_kindle_service(Settings())  # type: ignore[call-arg]
    service.send(args.paper, args.to)


def _today(args: argparse.Namespace) -> None:
    """Print one line per paper in the category's latest announcement.

    :param args: Parsed ``today`` arguments.
    :raises ValueError: If settings are invalid, the category is malformed or
        arXiv has no feed for it.
    :raises OSError: If the arXiv request fails.
    """
    service = build_listing_service(Settings())  # type: ignore[call-arg]
    papers = service.today(args.category)
    if not papers:
        print(
            f"No new papers in {args.category} today; arXiv announces none on "
            "weekends and holidays."
        )
    for paper in papers:
        mark = "[cross] " if paper.announce_type == "cross" else ""
        first_author = paper.authors[0] if paper.authors else "unknown author"
        print(f"{paper.arxiv_id}v{paper.version}  {mark}{paper.title} — {first_author}")


def _send(args: argparse.Namespace) -> None:
    """Mail the EPUB described by the ``send`` arguments.

    :param args: Parsed ``send`` arguments.
    :raises ValueError: If settings are invalid or delivery rejects the mail.
    :raises OSError: If the EPUB cannot be read or sending fails.
    """
    arxiv_id, version = args.id
    published_at = datetime.combine(args.published, time(), UTC)
    # Delivery reads only the ID, title, first author and year; the arXiv
    # client fills in the rest once it exists.
    paper = Paper(
        arxiv_id=arxiv_id,
        version=version,
        title=args.title,
        authors=tuple(args.author),
        abstract="",
        published_at=published_at,
        updated_at=published_at,
        license=None,
    )
    service = build_delivery_service(Settings())  # type: ignore[call-arg]
    service.send_epub(paper, args.epub.read_bytes(), args.to)


def _versioned_id(value: str) -> tuple[str, int]:
    """Split a versioned arXiv ID such as ``2401.01234v2``.

    :param value: The ID as typed.
    :returns: The ID without version and the version number.
    :raises argparse.ArgumentTypeError: If the ID has no version suffix.
    """
    match = VERSIONED_ID.fullmatch(value)
    if match is None:
        raise argparse.ArgumentTypeError(
            f"{value!r} is not a versioned arXiv ID such as 2401.01234v2"
        )
    return match["arxiv_id"], int(match["version"])


def _iso_date(value: str) -> date:
    """Parse a ``YYYY-MM-DD`` date.

    :param value: The date as typed.
    :returns: The date.
    :raises argparse.ArgumentTypeError: If the value is not ``YYYY-MM-DD``.
    """
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value!r} is not YYYY-MM-DD") from None


def _field(loc: tuple[int | str, ...]) -> str:
    """Name the setting a validation error refers to.

    :param loc: Location from a pydantic error, the field name first.
    :returns: The field name, or ``settings`` for errors on the whole model.
    """
    return str(loc[0]) if loc else "settings"
