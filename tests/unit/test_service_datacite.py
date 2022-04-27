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

def test_identifiers():
    SAMPLE_ATTRIBUTES = {
        'identifiers': [
            {
                'identifierType': 'ISNI',
                'identifier': 9783851254679
            },
        ]
    }

    assert datacite.identifiers_from_attributes( SAMPLE_ATTRIBUTES ) == [
        {
            'type': 'ISNI',
            'identifier': '9783851254679'
        }
    ]

def test_skip_invlaid_identifiers():
    INVALID_ATTRIBUTES = {
        'identifiers': [
            {
                'identifierType': 'ISBN',
                'identifier': "XXXXX"
            },
            {
                'identifierType': None,
                'identifier': 9783851254679
            },
        ]
    }

    assert datacite.identifiers_from_attributes( INVALID_ATTRIBUTES ) == [
        {
            'type': 'ISBN',
            'identifier': 'XXXXX'
        }
    ]
