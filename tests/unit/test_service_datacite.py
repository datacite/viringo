"""Unit tests for the DataCite service"""

from viringo.services import datacite

def test_strip_uri_prefix():
    """Test for the stripping of common prefixes from dois"""

    identifier = datacite.strip_uri_prefix("https://doi.org/10.5072/10002")
    assert identifier == "10.5072/10002"

    identifier = datacite.strip_uri_prefix("10.5072/10002")
    assert identifier == "10.5072/10002"

    identifier = datacite.strip_uri_prefix("")
    assert identifier == ""
