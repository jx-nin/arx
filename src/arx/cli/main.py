"""The ``arx`` command; its entry point configures logging (spec 8.1)."""

import argparse
import logging
import re
import sys
from collections.abc import Sequence
from datetime import UTC, date, datetime, time
from pathlib import Path

from arx.bootstrap import build_delivery_service
from arx.domain.paper import Paper
from arx.settings import Settings

VERSIONED_ID = re.compile(r"(?P<arxiv_id>.+)v(?P<version>[0-9]+)")


def main(argv: Sequence[str] | None = None) -> None:
    """Run the ``arx`` command.

    :param argv: Arguments without the program name; ``None`` reads
        ``sys.argv``.
    :raises SystemExit: On invalid arguments, a rejected delivery, invalid
        settings or a failed file or SMTP operation, with the reason.
    """
    args = _parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        _send(args)
    # ValidationError (settings) and the delivery rejections are ValueErrors;
    # smtplib errors are OSErrors.
    except (ValueError, OSError) as error:
        sys.exit(f"arx: {error}")


def _parser() -> argparse.ArgumentParser:
    """Build the argument parser.

    :returns: Parser for the ``send`` command.
    """
    parser = argparse.ArgumentParser(
        prog="arx", description="Fetch and read arXiv papers."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    send = commands.add_parser("send", help="e-mail an EPUB to a Kindle (FR-DLV-02)")
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
        type=date.fromisoformat,
        help="date the first version was published, YYYY-MM-DD",
    )
    return parser


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
