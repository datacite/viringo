"""Unit tests for the OAI-PMH DataCite Catalog implementation"""

from viringo import catalogs

def test_set_to_search_query():
    """Test for parsing a search query from a set"""

    search_query = catalogs.set_to_search_query(None)
    assert search_query is ""

    search_query = catalogs.set_to_search_query("DATACITE.BLOG")
    assert search_query is ""

    search_query = catalogs.set_to_search_query("DATACITE.BLOG~bGFzZXI=")
    assert search_query == "laser"

    search_query = catalogs.set_to_search_query("~bGFzZXI=")
    assert search_query == "laser"

    search_query = catalogs.set_to_search_query("DATACITE.BLOG~Y3JlYXRvcnMubmFtZUlkZW50aWZpZXJzLm5hbWVJZGVudGlmaWVyVHlwZTpPUkNJRA==")
    assert search_query == "creators.nameIdentifiers.nameIdentifierType:ORCID"

    search_query = catalogs.set_to_search_query("DATACITE~Y3JlYXRvcnMubmFtZUlkZW50aWZpZXJzLm5hbWVJZGVudGlmaWVyOio=")
    assert search_query == "creators.nameIdentifiers.nameIdentifier:*"

    search_query = catalogs.set_to_search_query("DATACITE~Y3JlYXRvcnMubmFtZUlkZW50aWZpZXJzLm5hbWVJZGVudGlmaWVyOio=")
    assert search_query == "creators.nameIdentifiers.nameIdentifier:*"


def test_set_to_provider_client():
    """Test for the converting a set to provider/client split"""

    provider_id, client_id = catalogs.set_to_provider_client("DATACITE.BLOG~cXVlcnk9bGFzZXI=")
    assert provider_id == "datacite"
    assert client_id == "datacite.blog"

    provider_id, client_id = catalogs.set_to_provider_client("DATACITE.BLOG")
    assert provider_id == "datacite"
    assert client_id == "datacite.blog"

    provider_id, client_id = catalogs.set_to_provider_client("datacite.blog")
    assert provider_id == "datacite"
    assert client_id == "datacite.blog"

    provider_id, client_id = catalogs.set_to_provider_client("")
    assert provider_id is None
    assert client_id is None

    provider_id, client_id = catalogs.set_to_provider_client("~cXVlcnk9bGFzZXI=")
    assert provider_id is None
    assert client_id is None

    provider_id, client_id = catalogs.set_to_provider_client(None)
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

def test_identifier_to_string_numeric():
    """Tests for converting an ISBN numeric identifier to single string"""

    identifier_type = {
        'type': 'ISBN',
        'identifier': "9783851254679"
    }

    identifier_string = catalogs.identifier_to_string(identifier_type)

    assert identifier_string == "isbn:9783851254679"
