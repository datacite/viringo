"""Tests for http endpoints of OAI-PMH verbs"""

import datetime
from lxml import etree

from . import factories

def construct_oai_xml_comparisons(fixture_file_path, target_xml, oai_element):
    """Return element xml strings for comparison based on fixture file and a target xml string"""
    # Load metadata from our file and the response
    # Pick out just the main chunk for comparison, header is different.
    fixture_et = etree.parse(fixture_file_path)

    metadata_a = fixture_et.getroot().find("./{http://www.openarchives.org/OAI/2.0/}" + oai_element)

    response_et = etree.fromstring(target_xml)
    metadata_b = response_et.find("./{http://www.openarchives.org/OAI/2.0/}" + oai_element)

    original = etree.tostring(metadata_a, encoding='unicode')
    target = etree.tostring(metadata_b, encoding='unicode')

    return original, target

def test_identify(client):
    """Test the identify verb responds and conforms as expected"""
    response = client.get('/')

    assert response.status_code == 200
    assert response.content_type == 'application/xml; charset=utf-8'

    # Compare just the verb part of the oai xml
    original, target = construct_oai_xml_comparisons(
        'tests/integration/fixtures/oai_identify.xml',
        response.get_data(),
        "Identify"
    )

    # Compare the main part of the request against test case
    assert original == target

def test_get_record_dc(client, mocker):
    """Test the getRecord verb responds and conforms as expected"""

    # Mock the datacite service to ensure the same record data is returned.
    mocked_get_metadata = mocker.patch('viringo.services.datacite.get_metadata')
    # Get fake result
    result = factories.MetadataFactory()
    # Set the mocked service to use the fake result
    mocked_get_metadata.return_value = result

    response = client.get('/?verb=GetRecord&metadataPrefix=oai_dc&identifier=doi:10.5072/not-a-real-doi')

    assert response.status_code == 200
    assert response.content_type == 'application/xml; charset=utf-8'

    # Compare just the verb part of the oai xml
    original, target = construct_oai_xml_comparisons(
        'tests/integration/fixtures/oai_getrecord_dc.xml',
        response.get_data(),
        "GetRecord"
    )

    # Compare the main part of the request against test case
    assert original == target

def test_list_records_dc(client, mocker):
    """Test the listRecords verb responds and conforms as expected"""

    # Mock the datacite service to ensure the same record data is returned.
    mocked_get_metadata_list = mocker.patch('viringo.services.datacite.get_metadata_list')
    # Get fake results
    result_1 = factories.MetadataFactory()
    result_2 = factories.MetadataFactory(
        identifier="10.5072/not-a-real-doi-2",
        created_datetime=datetime.datetime(2018, 5, 17, 6, 33),
        dates=[
            {'type': 'Issued', 'date': '2018-02-16'},
            {'type': 'Created', 'date': '2018-02-16'},
            {'type': 'Updated', 'date': '2018-02-16'}
        ],
        identifiers=[
            {'type': 'DOI', 'identifier': '10.5072/not-a-real-doi-2'}
        ],
        relations=[]
    )
    results = [result_1, result_2], 1

    # Set the mocked service to use the fake result
    mocked_get_metadata_list.return_value = results

    response = client.get('/?verb=ListRecords&metadataPrefix=oai_dc')

    assert response.status_code == 200
    assert response.content_type == 'application/xml; charset=utf-8'

    # Compare just the verb part of the oai xml
    original, target = construct_oai_xml_comparisons(
        'tests/integration/fixtures/oai_listrecords_dc.xml',
        response.get_data(),
        "ListRecords"
    )

    # Compare the main part of the request against test case
    assert original == target
