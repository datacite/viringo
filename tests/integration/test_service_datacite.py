"""Tests for DataCite service"""

import json
from viringo.services import datacite

# Mock the requests json return
def test_get_metadata():
    pass

# Mock the requests json return
def test_get_metadata_list():
    pass

def test_get_sets(mocker):
    # Mock the datacite service to ensure the same record data is returned.
    mocked_requests_get = mocker.patch('viringo.services.datacite.requests.get')

    with open('tests/integration/fixtures/datacite_api_clients.json') as json_file:
        data = json.load(json_file)

    # Set the mocked service to use the fake result
    mocked_requests_get.return_value.status_code = 200
    mocked_requests_get.return_value.json.return_value = data

    sets = datacite.get_sets()
    expected_sets = {'datacite.axiom': 'Axiom Data Science', 'datacite.datacite': 'DataCite', 'datacite.blog': 'DataCite Blog', 'datacite.transfer': 'DOI Transfer Client', 'datacite.force11': 'Force11', 'datacite.gtex': 'GTEx', 'datacite.lare': 'LA Referencia', 'datacite.neg': 'NASA Earthdata Group', 'datacite.dcppc': 'NIH Data Commons Pilot Phase Consortium', 'datacite.becker': 'Pascal Becker', 'datacite': 'DataCite'}

    assert sets == expected_sets