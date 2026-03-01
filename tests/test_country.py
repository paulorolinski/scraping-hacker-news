# tests/test_country.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from country import get_country_code, _extract_country_from_iana


class TestGetCountryCode:
    def test_united_states(self):
        assert get_country_code("United States") == "US"

    def test_united_kingdom(self):
        assert get_country_code("United Kingdom") == "GB"

    def test_moldova(self):
        assert get_country_code("Moldova") == "MD"

    def test_brazil(self):
        assert get_country_code("Brazil") == "BR"

    def test_remove_parentheses(self):
        # "Cayman Islands (the)" deve virar "Cayman Islands"
        assert get_country_code("Cayman Islands (the)") == "KY"

    def test_unknown_on_empty(self):
        assert get_country_code("") == "Unknown"

    def test_unknown_on_none(self):
        assert get_country_code(None) == "Unknown"

    def test_unknown_on_gibberish(self):
        assert get_country_code("xyzxyzxyz123") == "Unknown"


class TestExtractCountryFromIana:
    def test_extracts_last_address_line(self):
        text = (
            "organisation: ACME Registry\n"
            "address:      123 Some Street\n"
            "address:      Some City\n"
            "address:      Brazil\n"
        )
        assert _extract_country_from_iana(text) == "Brazil"

    def test_returns_unknown_when_no_block(self):
        assert _extract_country_from_iana("nothing useful here") == "Unknown"

    def test_ignores_block_without_organisation(self):
        text = (
            "remarks: some info\n"
            "address: United States\n"
        )
        assert _extract_country_from_iana(text) == "Unknown"