# tests/test_scraper.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from bs4 import BeautifulSoup
from scraper import _extract_domain, _parse_points, _parse_author, _parse_date, _parse_comments


class TestExtractDomain:
    def test_external_link(self):
        domain, tld = _extract_domain("https://github.com/user/repo")
        assert domain == "github.com"
        assert tld == ".com"

    def test_internal_hn_link(self):
        domain, tld = _extract_domain("item?id=12345")
        assert domain == "news.ycombinator.com"
        assert tld == ".com"

    def test_country_tld(self):
        domain, tld = _extract_domain("https://example.com.br/page")
        assert tld == ".com.br"

    def test_org_tld(self):
        domain, tld = _extract_domain("https://wikipedia.org/wiki/Python")
        assert domain == "wikipedia.org"
        assert tld == ".org"


class TestParsePoints:
    def _make_subtext(self, html):
        return BeautifulSoup(html, "html.parser")

    def test_parses_points(self):
        html = '<span class="score">142 points</span>'
        subtext = self._make_subtext(html)
        assert _parse_points(subtext) == 142

    def test_parses_single_point(self):
        html = '<span class="score">1 point</span>'
        subtext = self._make_subtext(html)
        assert _parse_points(subtext) == 1


class TestParseAuthor:
    def _make_subtext(self, html):
        return BeautifulSoup(html, "html.parser")

    def test_parses_author(self):
        html = '<a class="hnuser">pg</a>'
        subtext = self._make_subtext(html)
        assert _parse_author(subtext) == "pg"

    def test_fallback_when_missing(self):
        subtext = BeautifulSoup("", "html.parser")
        assert _parse_author(subtext) == "Desconhecido"


class TestParseComments:
    def _make_subtext(self, html):
        return BeautifulSoup(html, "html.parser")

    def test_parses_comments(self):
        html = '<a href="#">57 comments</a>'
        subtext = self._make_subtext(html)
        assert _parse_comments(subtext) == 57

    def test_zero_when_no_comments_link(self):
        html = '<a href="#">discuss</a>'
        subtext = self._make_subtext(html)
        assert _parse_comments(subtext) == 0

    def test_zero_when_empty(self):
        subtext = BeautifulSoup("", "html.parser")
        assert _parse_comments(subtext) == 0