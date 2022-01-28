import json
from viringo import catalogs
from viringo.services import datacite
def test_build_metadata_null_dates(mocker):
    mocked_requests_get = mocker.patch('viringo.services.datacite.requests.get')
    with open('tests/integration/fixtures/datacite_api_doi_dateproblems.json') as json_file:
        data = json.load(json_file)
    mocked_requests_get.return_value.status_code = 200
    mocked_requests_get.return_value.json.return_value = data

    result = datacite.get_metadata("10.5438/prvv-nv23")

    oai_server  = catalogs.DataCiteOAIServer()
    meta = oai_server.build_metadata_map(
        result
    )
    assert meta.get('date') == ['2018', 'Updated: 2018-01-18']
