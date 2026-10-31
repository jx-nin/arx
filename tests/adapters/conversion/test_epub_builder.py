import logging
import zipfile
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path

import pytest

from arx.adapters.conversion.epub_builder import KINDLE_CSS, PandocEpubBuilder
from arx.domain.paper import Paper

HTML = """<!DOCTYPE html>
<html><head><title>ignored</title></head><body>
<h2>1 Introduction</h2><p>Long documents strain dense attention.</p>
<h2>2 Method</h2><p>We keep the top-k keys per query.</p>
</body></html>"""

PAPER = Paper(
    arxiv_id="2401.01234",
    version=2,
    title="Sparse Attention for Long Documents",
    authors=("Ada Lovelace", "Alan Turing"),
    abstract="We study sparse attention.",
    published_at=datetime(2024, 1, 3, tzinfo=UTC),
    updated_at=datetime(2024, 2, 14, tzinfo=UTC),
    license=None,
)


@pytest.fixture(scope="module")
def epub() -> zipfile.ZipFile:
    return zipfile.ZipFile(BytesIO(PandocEpubBuilder().build(HTML, PAPER)))


def read(epub: zipfile.ZipFile, suffix: str) -> str:
    names = [name for name in epub.namelist() if name.endswith(suffix)]
    assert names, f"no {suffix} in {epub.namelist()}"
    return "\n".join(epub.read(name).decode() for name in names)


@pytest.mark.req("FR-CNV-01")
def test_builds_an_epub3_package(epub: zipfile.ZipFile) -> None:
    assert epub.namelist()[0] == "mimetype"
    assert epub.read("mimetype") == b"application/epub+zip"
    assert 'version="3.0"' in read(epub, ".opf")


@pytest.mark.req("FR-CNV-01")
@pytest.mark.parametrize(
    "expected",
    [
        ">Sparse Attention for Long Documents</dc:title>",
        ">Ada Lovelace</dc:creator>",
        ">Alan Turing</dc:creator>",
        ">2024-01-03",
        "<dc:language>en</dc:language>",
    ],
)
def test_package_metadata_comes_from_the_paper(
    epub: zipfile.ZipFile, expected: str
) -> None:
    assert expected in read(epub, ".opf")


@pytest.mark.req("FR-CNV-01")
@pytest.mark.parametrize("heading", ["1 Introduction", "2 Method"])
def test_table_of_contents_lists_sections(epub: zipfile.ZipFile, heading: str) -> None:
    assert heading in read(epub, "nav.xhtml")


@pytest.mark.req("FR-CNV-01")
def test_embeds_the_kindle_stylesheet(epub: zipfile.ZipFile) -> None:
    assert KINDLE_CSS.read_text().strip() in read(epub, ".css")


@pytest.mark.req("FR-CNV-01")
def test_logs_pandoc_warnings(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING):
        PandocEpubBuilder().build('<p><img src="missing.png"></p>', PAPER)

    assert "missing.png" in caplog.text


@pytest.mark.req("FR-CNV-01")
def test_does_not_embed_files_relative_to_the_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "secret.png").write_bytes(b"\x89PNG secret")
    monkeypatch.chdir(tmp_path)

    epub = zipfile.ZipFile(
        BytesIO(PandocEpubBuilder().build('<p><img src="secret.png"></p>', PAPER))
    )

    assert not [name for name in epub.namelist() if "media" in name]
