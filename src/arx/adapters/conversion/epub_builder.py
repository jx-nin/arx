"""EPUB builder backed by the pandoc command line tool (spec 6.5.1 step 9)."""

import logging
import subprocess
import tempfile
from importlib import resources
from pathlib import Path

from arx.domain.paper import Paper

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 60
# arXiv papers carry no language field; nearly all are English.
LANGUAGE = "en"
KINDLE_CSS = resources.files(__package__) / "kindle.css"


class PandocEpubBuilder:
    """Builds EPUB 3 files with pandoc and the Kindle stylesheet."""

    def build(self, html: str, paper: Paper) -> bytes:
        """Build an EPUB 3 file with a two-level table of contents.

        :param html: Complete HTML document: title page followed by the body.
        :param paper: Paper whose title, authors and date go into the package.
        :returns: The EPUB file contents.
        :raises FileNotFoundError: If pandoc is not on ``PATH``.
        :raises subprocess.CalledProcessError: If pandoc exits with an error;
            its ``stderr`` holds pandoc's diagnostics.
        :raises subprocess.TimeoutExpired: If pandoc runs longer than
            :data:`TIMEOUT_SECONDS`.
        """
        with resources.as_file(KINDLE_CSS) as css, tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "paper.epub"
            # Repeated --metadata author=... values become a list in pandoc.
            authors = [f"--metadata=author={name}" for name in paper.authors]
            # shortcut: pandoc still embeds absolute img src paths and fetches URLs;
            # remove once sanitising (spec 6.5.1 step 2) or ADR-009 isolation lands.
            result = subprocess.run(
                [
                    "pandoc",
                    "--from=html",
                    "--to=epub3",
                    "--toc",
                    "--toc-depth=2",
                    "--epub-title-page=false",
                    f"--css={css}",
                    f"--metadata=title={paper.title}",
                    *authors,
                    f"--metadata=date={paper.published_at.date().isoformat()}",
                    f"--metadata=lang={LANGUAGE}",
                    f"--output={output}",
                ],
                input=html,
                encoding="utf-8",
                capture_output=True,
                check=True,
                timeout=TIMEOUT_SECONDS,
                cwd=tmp,
            )
            if result.stderr:
                logger.warning("pandoc: %s", result.stderr.strip())
            return output.read_bytes()
