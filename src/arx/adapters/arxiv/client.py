"""arXiv client: API metadata, RSS listings and HTML renditions (spec 6.6.1)."""

import logging
import re
import time
from collections.abc import Callable
from datetime import datetime

import httpx
from lxml import etree

from arx.domain.announcement import Announcement
from arx.domain.arxiv_id import ID_PATTERN
from arx.domain.paper import Paper

logger = logging.getLogger(__name__)

# shortcut: fixed endpoints, move to ARX_ARXIV_*_BASE settings (spec 12) in M1.
API_URL = "https://export.arxiv.org/api/query"
HTML_URL = "https://arxiv.org/html/{versioned_id}"
RSS_URL = "https://rss.arxiv.org/rss/{category}"
ATOM = {"atom": "http://www.w3.org/2005/Atom"}
RSS = {
    "arxiv": "http://arxiv.org/schemas/atom",
    "dc": "http://purl.org/dc/elements/1.1/",
}
# Error reports come as entries whose ID is not a paper URL.
ENTRY_ID = re.compile(
    rf"https?://arxiv\.org/abs/(?P<arxiv_id>{ID_PATTERN})v(?P<version>[1-9][0-9]*)"
)
ITEM_GUID = re.compile(
    rf"oai:arXiv\.org:(?P<arxiv_id>{ID_PATTERN})v(?P<version>[1-9][0-9]*)"
)
# Innermost parenthesised group: affiliations follow author names in the feed.
AFFILIATION = re.compile(r"\s*\([^()]*\)")


class ArxivClient:
    """Fetches papers from arXiv, one request at a time.

    Requests are spaced by a minimum interval (M0 exception in spec 6.6.1);
    the rate limiter replaces the wait in M1.
    """

    def __init__(
        self,
        http: httpx.Client,
        min_interval: float,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Create the client.

        :param http: HTTP client with the identifying ``User-Agent`` set.
        :param min_interval: Minimum seconds between the starts of two requests.
        :param sleep: Function that waits the given seconds.
        :param clock: Monotonic clock in seconds.
        """
        self._http = http
        self._min_interval = min_interval
        self._sleep = sleep
        self._clock = clock
        self._last_request: float | None = None

    def paper(self, arxiv_id: str, version: int | None) -> Paper | None:
        """Look up a paper's metadata in the arXiv API.

        :param arxiv_id: arXiv identifier without version suffix.
        :param version: Version to look up, or ``None`` for the latest.
        :returns: The paper, or ``None`` if arXiv has no such paper.
        :raises ValueError: If the API answers with an error entry.
        :raises OSError: If the request fails.
        """
        id_list = arxiv_id if version is None else f"{arxiv_id}v{version}"
        response = self._get(API_URL, params={"id_list": id_list})
        return None if response is None else _parse_entry(response.content)

    def announcements(self, category: str) -> list[Announcement]:
        """Read the category's RSS feed of the latest daily announcement.

        :param category: arXiv category such as ``cs.LG``, already checked.
        :returns: The announced papers in feed order; empty on days without
            announcement.
        :raises ValueError: If arXiv has no feed for the category, the body is
            not XML or an item carries no arXiv ID.
        :raises OSError: If the request fails, also on an unknown category.
        """
        response = self._get(RSS_URL.format(category=category))
        if response is None:
            raise ValueError(f"arXiv has no feed for {category}")
        return _parse_rss(response.content)

    def html(self, paper: Paper) -> str | None:
        """Download the HTML rendition of the paper's version.

        :param paper: Paper whose rendition to fetch.
        :returns: The HTML page, or ``None`` if arXiv has no rendition.
        :raises OSError: If the request fails.
        """
        url = HTML_URL.format(versioned_id=f"{paper.arxiv_id}v{paper.version}")
        response = self._get(url)
        return None if response is None else response.text

    def _get(
        self, url: str, params: dict[str, str] | None = None
    ) -> httpx.Response | None:
        """Send a GET request after waiting out the minimum interval.

        :param url: URL to fetch.
        :param params: Query parameters.
        :returns: The response, or ``None`` on 404.
        :raises OSError: On a network error or any other error status.
        """
        if self._last_request is not None:
            wait = self._min_interval - (self._clock() - self._last_request)
            if wait > 0:
                self._sleep(wait)
        self._last_request = self._clock()
        try:
            response = self._http.get(url, params=params)
            if response.status_code == httpx.codes.NOT_FOUND:
                return None
            response.raise_for_status()
        except httpx.HTTPError as error:
            # httpx appends a second line pointing to the MDN status page.
            reason = str(error).partition("\n")[0]
            raise OSError(f"arXiv request failed: {reason}") from error
        logger.debug("GET %s -> %d", url, response.status_code)
        return response


def _parse_entry(atom: bytes) -> Paper | None:
    """Read the first entry of an arXiv API Atom feed.

    :param atom: The response body.
    :returns: The paper, or ``None`` if the feed has no entry.
    :raises ValueError: If the body is not XML or the entry is an API error
        report.
    """
    entry = _xml(atom, "API").find("atom:entry", ATOM)
    if entry is None:
        return None
    match = ENTRY_ID.fullmatch(_text(entry, "id"))
    if match is None:
        raise ValueError(f"arXiv API error: {_text(entry, 'summary')}")
    return Paper(
        arxiv_id=match["arxiv_id"],
        version=int(match["version"]),
        title=_text(entry, "title"),
        authors=tuple(
            " ".join(name.split())
            for name in entry.xpath("atom:author/atom:name/text()", namespaces=ATOM)
        ),
        abstract=_text(entry, "summary"),
        published_at=datetime.fromisoformat(_text(entry, "published")),
        updated_at=datetime.fromisoformat(_text(entry, "updated")),
        # The API does not carry the licence.
        license=None,
    )


def _parse_rss(rss: bytes) -> list[Announcement]:
    """Read the items of an arXiv category RSS feed.

    :param rss: The response body.
    :returns: One announcement per item, in feed order.
    :raises ValueError: If the body is not XML or an item's ``guid`` is not an
        ``oai:arXiv.org:<id>v<n>`` identifier.
    """
    announcements = []
    for item in _xml(rss, "RSS").iterfind("channel/item"):
        guid = item.findtext("guid", "")
        match = ITEM_GUID.fullmatch(guid.strip())
        if match is None:
            raise ValueError(f"arXiv RSS item without arXiv ID: {guid!r}")
        announcements.append(
            Announcement(
                arxiv_id=match["arxiv_id"],
                version=int(match["version"]),
                title=" ".join(item.findtext("title", "").split()),
                authors=_authors(item.findtext("dc:creator", "", RSS)),
                announce_type=item.findtext("arxiv:announce_type", "", RSS).strip(),
            )
        )
    return announcements


def _authors(creators: str) -> tuple[str, ...]:
    """Split an RSS item's comma-separated authors, dropping affiliations.

    :param creators: Text of ``<dc:creator>``, e.g. ``A (Univ, Dept), B``.
    :returns: Author names in listing order.
    """
    while AFFILIATION.search(creators):
        creators = AFFILIATION.sub("", creators)
    return tuple(" ".join(n.split()) for n in creators.split(",") if n.strip())


def _xml(body: bytes, source: str) -> etree._Element:
    """Parse an untrusted XML response: no entity expansion, no network access.

    :param body: The response body.
    :param source: Name of the arXiv interface for the error message.
    :returns: The root element.
    :raises ValueError: If the body is not well-formed XML.
    """
    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    try:
        return etree.fromstring(body, parser)
    except etree.XMLSyntaxError as error:
        raise ValueError(f"arXiv {source} returned malformed XML: {error}") from error


def _text(entry: etree._Element, tag: str) -> str:
    """Return an Atom child element's text on one line.

    :param entry: The ``<entry>`` element.
    :param tag: Atom tag name without namespace.
    :returns: The text with runs of whitespace collapsed, or ``""``.
    """
    return " ".join((entry.findtext(f"atom:{tag}", "", ATOM)).split())
