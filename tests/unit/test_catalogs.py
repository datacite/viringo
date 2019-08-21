"""Unit tests for the OAI-PMH DataCite Catalog implementation"""

from viringo import catalogs

def test_set_to_provider_client():
    """Test for the converting a set to provider/client split"""

    provider_id, client_id = catalogs.set_to_provider_client("DATACITE.BLOG")
    assert provider_id == "datacite"
    assert client_id == "datacite.blog"

    provider_id, client_id = catalogs.set_to_provider_client("datacite.blog")
    assert provider_id == "datacite"
    assert client_id == "datacite.blog"

    provider_id, client_id = catalogs.set_to_provider_client("")
    assert provider_id is None
    assert client_id is None

def test_identifier_to_string():
    """Tests for converting identifier to single string"""

    identifier_type = {
        'type': 'DOI',
        'identifier': "10.5072/1234"
    }

    identifier_string = catalogs.identifier_to_string(identifier_type)

    assert identifier_string == "doi:10.5072/1234"