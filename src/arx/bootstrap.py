"""Composition root: builds services with their concrete adapters (spec 5.2)."""

from importlib.metadata import version

import httpx
from sqlalchemy import Engine, create_engine, make_url

from arx.adapters.arxiv.client import ArxivClient
from arx.adapters.conversion.epub_builder import PandocEpubBuilder
from arx.adapters.conversion.html_cleaner import LatexmlHtmlCleaner
from arx.adapters.mail.smtp_mailer import SmtpMailer
from arx.services.conversion import ConversionService
from arx.services.delivery import DeliveryService
from arx.services.kindle import KindleService
from arx.services.listing import ListingService
from arx.settings import DatabaseSettings, Settings

ARXIV_TIMEOUT_SECONDS = 30.0


def build_delivery_service(settings: Settings) -> DeliveryService:
    """Build the delivery service with the SMTP mailer (spec 6.6.3).

    :param settings: Loaded configuration.
    :returns: A service that mails EPUBs through the configured SMTP server.
    """
    mailer = SmtpMailer(
        settings.smtp_host,
        settings.smtp_port,
        settings.smtp_username,
        settings.smtp_password_file,
    )
    return DeliveryService(
        mailer,
        settings.delivery_from,
        settings.delivery_allowed_recipients,
        settings.delivery_max_bytes,
    )


def build_arxiv_client(settings: Settings) -> ArxivClient:
    """Build the arXiv client with an identifying ``User-Agent`` (spec 6.6.1).

    :param settings: Loaded configuration.
    :returns: A client that spaces requests by the configured interval.
    """
    user_agent = settings.arxiv_user_agent or (
        f"arx/{version('arx')} (mailto:{settings.delivery_from})"
    )
    # shortcut: never closed, fine for one CLI run; close it when the worker owns it.
    http = httpx.Client(
        headers={"User-Agent": user_agent},
        timeout=ARXIV_TIMEOUT_SECONDS,
        follow_redirects=True,
    )
    return ArxivClient(http, settings.arxiv_min_interval_s)


def build_kindle_service(settings: Settings) -> KindleService:
    """Build the send-to-Kindle service from arXiv, pandoc and SMTP adapters.

    :param settings: Loaded configuration.
    :returns: A service that fetches, converts and mails one paper.
    """
    conversion = ConversionService(LatexmlHtmlCleaner(), PandocEpubBuilder())
    return KindleService(
        build_arxiv_client(settings), conversion, build_delivery_service(settings)
    )


def build_listing_service(settings: Settings) -> ListingService:
    """Build the daily listing service on the arXiv client.

    :param settings: Loaded configuration.
    :returns: A service that lists a category's latest announced papers.
    """
    return ListingService(build_arxiv_client(settings))


def build_engine(settings: DatabaseSettings) -> Engine:
    """Build the SQLAlchemy engine for PostgreSQL over psycopg 3 (Q-11).

    :param settings: Database configuration.
    :returns: An engine that connects lazily, on first use.
    :raises OSError: If the URL file cannot be read.
    :raises sqlalchemy.exc.ArgumentError: If the file does not hold a valid URL.
    """
    url = make_url(settings.database_url_file.read_text().strip())
    # A plain postgresql:// URL would select psycopg2, which is not installed.
    return create_engine(url.set(drivername="postgresql+psycopg"))
