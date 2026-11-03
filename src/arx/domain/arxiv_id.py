"""arXiv identifiers and the references the owner pastes for them (FR-ING-04)."""

import re
from dataclasses import dataclass

# New-style IDs (2401.01234) and old-style ones (hep-th/9901001, math.GT/0309136).
ID_PATTERN = r"[0-9]{4}\.[0-9]{4,5}|[a-z-]+(?:\.[A-Z]{2})?/[0-9]{7}"
VERSIONED_ID = re.compile(rf"(?P<arxiv_id>{ID_PATTERN})v(?P<version>[1-9][0-9]*)")
REFERENCE = re.compile(
    r"(?:(?i:arxiv:)|(?i:(?:https?://)?(?:www\.)?arxiv\.org/(?:abs|pdf|html)/))?"
    rf"(?P<arxiv_id>{ID_PATTERN})(?:v(?P<version>[1-9][0-9]*))?(?:\.pdf|/)?"
)


@dataclass(frozen=True)
class PaperRef:
    """A paper named by the owner, at one version or the latest.

    :param arxiv_id: arXiv identifier without version suffix.
    :param version: Version number, or ``None`` for the latest version.
    """

    arxiv_id: str
    version: int | None


def parse_reference(text: str) -> PaperRef:
    """Read an arXiv ID or an abstract, PDF or HTML URL.

    :param text: ID such as ``2401.01234v2`` or ``arXiv:2401.01234``, or a URL
        such as ``https://arxiv.org/abs/2401.01234``; surrounding whitespace is
        ignored.
    :returns: The paper and version the text names.
    :raises ValueError: If the text names no arXiv paper.
    """
    match = REFERENCE.fullmatch(text.strip())
    if match is None:
        raise ValueError(f"{text!r} is not an arXiv ID or abs, pdf or html URL")
    version = match["version"]
    return PaperRef(match["arxiv_id"], int(version) if version else None)
