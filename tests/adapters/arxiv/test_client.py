from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest

from arx.adapters.arxiv.client import ArxivClient
from arx.domain.paper import Paper

FIXTURES = Path(__file__).parents[2] / "fixtures" / "arxiv"
PAPER = Paper(
    arxiv_id="2401.01234",
    version=1,
    title="Mixture cure semiparametric additive hazard models",
    authors=("Jinqing Li", "Jun Ma"),
    abstract="",
    published_at=datetime(2024, 1, 2, tzinfo=UTC),
    updated_at=datetime(2024, 1, 2, tzinfo=UTC),
    license=None,
)


class FakeClock:
    def __init__(self) -> None:
        self.now = 100.0
        self.sleeps: list[float] = []

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


def make_client(
    handler: httpx.MockTransport | None = None,
    responses: dict[str, httpx.Response] | None = None,
    clock: FakeClock | None = None,
) -> tuple[ArxivClient, list[httpx.Request]]:
    requests: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return (responses or {}).get(request.url.path, httpx.Response(404))

    http = httpx.Client(transport=handler or httpx.MockTransport(respond))
    fake = clock or FakeClock()
    return ArxivClient(http, 3.0, sleep=fake.sleep, clock=fake), requests


def api_response(fixture: str) -> dict[str, httpx.Response]:
    content = (FIXTURES / fixture).read_bytes()
    return {"/api/query": httpx.Response(200, content=content)}


@pytest.mark.contract
@pytest.mark.req("FR-ING-04")
def test_paper_reads_the_api_entry() -> None:
    client, requests = make_client(responses=api_response("api_2401.01234.xml"))

    paper = client.paper("2401.01234", None)

    assert paper is not None
    assert (paper.arxiv_id, paper.version) == ("2401.01234", 1)
    assert paper.title.startswith("Mixture cure semiparametric additive hazard")
    assert paper.authors == ("Jinqing Li", "Jun Ma")
    assert paper.abstract.startswith("Survival analysis can sometimes involve")
    assert "\n" not in paper.abstract
    assert paper.published_at == datetime(2024, 1, 2, 15, 2, 42, tzinfo=UTC)
    assert paper.license is None
    [request] = requests
    assert request.url.host == "export.arxiv.org"
    assert request.url.params["id_list"] == "2401.01234"


@pytest.mark.contract
@pytest.mark.req("FR-ING-04")
def test_paper_without_version_is_the_latest_one() -> None:
    client, _ = make_client(responses=api_response("api_1706.03762.xml"))

    paper = client.paper("1706.03762", None)

    assert paper is not None
    assert (paper.version, paper.title) == (7, "Attention Is All You Need")
    assert paper.published_at == datetime(2017, 6, 12, 17, 57, 34, tzinfo=UTC)
    assert paper.updated_at == datetime(2023, 8, 2, 0, 41, 18, tzinfo=UTC)


@pytest.mark.req("FR-ING-04")
def test_paper_asks_for_the_requested_version() -> None:
    client, requests = make_client(responses=api_response("api_2401.01234.xml"))

    client.paper("2401.01234", 1)

    assert requests[0].url.params["id_list"] == "2401.01234v1"


@pytest.mark.contract
@pytest.mark.req("FR-ING-04")
def test_paper_is_none_when_arxiv_has_no_such_paper() -> None:
    client, _ = make_client(responses=api_response("api_missing.xml"))

    assert client.paper("2401.99999", None) is None


@pytest.mark.contract
@pytest.mark.req("FR-ING-04")
def test_paper_reports_an_api_error_entry() -> None:
    client, _ = make_client(responses=api_response("api_error.xml"))

    with pytest.raises(ValueError, match="incorrect id format for 2401.1"):
        client.paper("2401.1", None)


@pytest.mark.req("FR-ING-04")
def test_html_downloads_the_rendition_of_that_version() -> None:
    page = httpx.Response(200, text="<html>paper</html>")
    client, requests = make_client(responses={"/html/2401.01234v1": page})

    assert client.html(PAPER) == "<html>paper</html>"
    assert requests[0].url.host == "arxiv.org"


@pytest.mark.req("FR-ING-04")
def test_html_is_none_without_a_rendition() -> None:
    client, _ = make_client()

    assert client.html(PAPER) is None


@pytest.mark.req("FR-ING-04")
def test_server_errors_raise_os_error() -> None:
    client, _ = make_client(responses={"/html/2401.01234v1": httpx.Response(503)})

    with pytest.raises(OSError, match="503"):
        client.html(PAPER)


@pytest.mark.req("FR-ING-04")
def test_network_errors_raise_os_error() -> None:
    def fail(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no route", request=request)

    client, _ = make_client(handler=httpx.MockTransport(fail))

    with pytest.raises(OSError, match="no route"):
        client.html(PAPER)


@pytest.mark.req("NFR-16")
def test_requests_are_spaced_by_the_minimum_interval() -> None:
    clock = FakeClock()
    client, _ = make_client(clock=clock)

    client.html(PAPER)
    clock.now += 1.0
    client.html(PAPER)
    clock.now += 5.0
    client.html(PAPER)

    assert clock.sleeps == [2.0]
