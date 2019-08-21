"""Tests for DataCite service"""

import json
from viringo.services import datacite

# Mock the requests json return
def test_get_metadata(mocker):
    """Tests the results of the datasite service for getting a single metadata record"""
    # Mock the datacite service to ensure the same record data is returned.
    mocked_requests_get = mocker.patch('viringo.services.datacite.requests.get')

    with open('tests/integration/fixtures/datacite_api_doi.json') as json_file:
        data = json.load(json_file)

    # Set the mocked service to use the fake result
    mocked_requests_get.return_value.status_code = 200
    mocked_requests_get.return_value.json.return_value = data

    metadata = datacite.get_metadata("10.5438/prvv-nv23")

    # Compare some key elements to see if it's what we expect
    assert metadata.identifier == "10.5438/prvv-nv23"
    assert metadata.titles == ['Welcome to the DataCite Team, Richard!']
    assert metadata.creators == ['Fenner, Martin', 'Hallett, Richard']
    assert metadata.descriptions == ['DataCite is pleased to welcome Richard \
Hallett to our team. Richard joined DataCite as application developer \
in December. Get to know him better via this interview. Richard Hallett \
Can you tell us a little bit about what you did before you started...']
    assert metadata.subjects == ['datacite']
    assert metadata.publisher == 'DataCite'
    assert metadata.publication_year == 2018
    assert metadata.dates == [
        {'type': 'Issued', 'date': '2018-01-18'},
        {'type': 'Created', 'date': '2018-01-18'},
        {'type': 'Updated', 'date': '2018-01-18'}
    ]
    assert metadata.resource_types == ['Text']
    assert metadata.identifiers == [{'type': 'DOI', 'identifier': '10.5438/prvv-nv23'}]
    assert metadata.relations == [{'type': 'DOI', 'identifier': '10.5438/0000-00ss'}]
    assert metadata.client == 'DATACITE.BLOG'
    assert metadata.active


# Mock the requests json return
def test_get_metadata_list(mocker):
    """Tests the results of the datasite service for getting a list of metadata records"""
    # Mock the datacite service to ensure the same record data is returned.
    mocked_requests_get = mocker.patch('viringo.services.datacite.requests.get')

    with open('tests/integration/fixtures/datacite_api_dois.json') as json_file:
        data = json.load(json_file)

    # Set the mocked service to use the fake result
    mocked_requests_get.return_value.status_code = 200
    mocked_requests_get.return_value.json.return_value = data

    # We don't need cursor in the test
    metadata_list, _ = datacite.get_metadata_list(client_id="datacite.datacite")

    assert len(metadata_list) == 25


def test_get_sets(mocker):
    """Tests the results of the datasite service for getting a list of sets"""
    # Mock the datacite service to ensure the same record data is returned.
    mocked_requests_get = mocker.patch('viringo.services.datacite.requests.get')

    with open('tests/integration/fixtures/datacite_api_clients.json') as json_file:
        data = json.load(json_file)

    # Set the mocked service to use the fake result
    mocked_requests_get.return_value.status_code = 200
    mocked_requests_get.return_value.json.return_value = data

    sets = datacite.get_sets()
    expected_sets = [
        ('datacite', 'DataCite'),
        ('datacite.axiom', 'Axiom Data Science'),
        ('datacite.becker', 'Pascal Becker'),
        ('datacite.blog', 'DataCite Blog'),
        ('datacite.datacite', 'DataCite'),
        ('datacite.dcppc', 'NIH Data Commons Pilot Phase Consortium'),
        ('datacite.force11', 'Force11'),
        ('datacite.gtex', 'GTEx'),
        ('datacite.lare', 'LA Referencia'),
        ('datacite.neg', 'NASA Earthdata Group'),
        ('datacite.transfer', 'DOI Transfer Client')
    ]

    assert sets == expected_sets
