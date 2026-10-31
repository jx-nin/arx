"""HTML cleaner for LaTeXML renditions served by arXiv (spec 6.5.1 step 3)."""

from lxml import etree
from lxml import html as lxml_html

# LaTeXML front matter that the title page already shows.
FRONT_MATTER_CLASSES = ("ltx_title_document", "ltx_authors", "ltx_abstract")


class LatexmlHtmlCleaner:
    """Extracts the paper body from an arXiv HTML page."""

    def article(self, html: str) -> str:
        """Return the ``<article>`` element without page chrome or front matter.

        :param html: The HTML rendition as served by arXiv.
        :returns: The article markup, tags included.
        :raises ValueError: If the HTML has no ``<article>`` element.
        """
        try:
            document = lxml_html.document_fromstring(html)
        except etree.ParserError as error:
            raise ValueError("HTML rendition has no <article> element") from error
        article = document.find(".//article")
        if article is None:
            raise ValueError("HTML rendition has no <article> element")
        for class_name in FRONT_MATTER_CLASSES:
            for element in article.find_class(class_name):
                element.drop_tree()
        return lxml_html.tostring(article, encoding="unicode")
