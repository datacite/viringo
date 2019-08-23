"""Unit tests for the OAI-PMH DataCite Catalog implementation"""

from viringo import catalogs

def test_set_to_search_query():
    """Test for parsing a search query from a set"""

    search_query = catalogs.set_to_search_query(None)
    assert search_query == None

    search_query = catalogs.set_to_search_query("DATACITE.BLOG")
    assert search_query == None

    search_query = catalogs.set_to_search_query("DATACITE.BLOG~cXVlcnk9bGFzZXI=")
    assert search_query == "query=laser"

    search_query = catalogs.set_to_search_query("~cXVlcnk9bGFzZXI=")
    assert search_query == "query=laser"

    search_query = catalogs.set_to_search_query("DATACITE.BLOG~cXVlcnk9Y3JlYXRvcnMubmFtZUlkZW50aWZpZXJzLm5hbWVJZGVudGlmaWVyVHlwZTpPUkNJRA==")
    assert search_query == "query=creators.nameIdentifiers.nameIdentifierType:ORCID"

    search_query = catalogs.set_to_search_query("DATACITE~cXVlcnk9Y3JlYXRvcnMubmFtZUlkZW50aWZpZXJzLm5hbWVJZGVudGlmaWVyOio=")
    assert search_query == "query=creators.nameIdentifiers.nameIdentifier:*"

    search_query = catalogs.set_to_search_query("DATACITE~cXVlcnk9Y3JlYXRvcnMubmFtZUlkZW50aWZpZXJzLm5hbWVJZGVudGlmaWVyOio=")
    assert search_query == "query=creators.nameIdentifiers.nameIdentifier:*"


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