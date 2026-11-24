"""Tests for http endpoints of OAI-PMH verbs"""

import datetime
import pytest
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

    original = ''
    target = ''
    if metadata_a is not None:
        original = etree.tostring(metadata_a, encoding='unicode', pretty_print=True)

    if metadata_b is not None:
        target = etree.tostring(metadata_b, encoding='unicode', pretty_print=True)

    return original, target

def test_identify(client):
    """Test the identify verb responds and conforms as expected"""
    response = client.get('/oai')

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
    """Test the getRecord verb responds and conforms as expected in dc format"""

    # Mock the datacite service to ensure the same record data is returned.
    mocked_get_metadata = mocker.patch('viringo.services.datacite.get_metadata')
    # Get fake result
    result = factories.MetadataFactory()
    # Set the mocked service to use the fake result
    mocked_get_metadata.return_value = result

    response = client.get(
        '/oai?verb=GetRecord&metadataPrefix=oai_dc&identifier=doi:10.5072/not-a-real-doi'
    )

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

def test_get_record_oai_datacite(client, mocker):
    """Test the getRecord verb responds and conforms as expected in oai_datacite format"""

    # Mock the datacite service to ensure the same record data is returned.
    mocked_get_metadata = mocker.patch('viringo.services.datacite.get_metadata')
    # Get fake result
    result = factories.MetadataFactory()
    # Set the mocked service to use the fake result
    mocked_get_metadata.return_value = result

    response = client.get(
        '/oai?verb=GetRecord&metadataPrefix=oai_datacite&identifier=doi:10.5072/not-a-real-doi'
    )

    assert response.status_code == 200
    assert response.content_type == 'application/xml; charset=utf-8'

    # Compare just the verb part of the oai xml
    original, target = construct_oai_xml_comparisons(
        'tests/integration/fixtures/oai_getrecord_oaidatacite.xml',
        response.get_data(),
        "GetRecord"
    )

    # Compare the main part of the request against test case
    assert original == target

def test_get_record_invalid_xml_oai_datacite(client, mocker):
    """Test the getRecord verb responds and conforms as expected in oai_datacite format with XML with invalid characters"""

    # Mock the datacite service to ensure the same record data is returned.
    mocked_get_metadata = mocker.patch('viringo.services.datacite.get_metadata')
    # Get fake result
    result = factories.InvalidXMLMetadataFactory()
    # Set the mocked service to use the fake result
    mocked_get_metadata.return_value = result

    response = client.get(
        '/oai?verb=GetRecord&metadataPrefix=oai_datacite&identifier=doi:10.5072/not-a-real-doi'
    )

    assert response.status_code == 200
    assert response.content_type == 'application/xml; charset=utf-8'

    # Compare just the verb part of the oai xml
    original, target = construct_oai_xml_comparisons(
        'tests/integration/fixtures/oai_getrecord_oaidatacite_invalid.xml',
        response.get_data(),
        "GetRecord"
    )

    # Compare the main part of the request against test case
    assert original == target    

def test_get_record_datacite(client, mocker):
    """Test the getRecord verb responds and conforms as expected in datacite format"""

    # Mock the datacite service to ensure the same record data is returned.
    mocked_get_metadata = mocker.patch('viringo.services.datacite.get_metadata')
    # Get fake result
    result = factories.MetadataFactory()
    # Set the mocked service to use the fake result
    mocked_get_metadata.return_value = result

    response = client.get(
        '/oai?verb=GetRecord&metadataPrefix=datacite&identifier=doi:10.5072/not-a-real-doi'
    )

    assert response.status_code == 200
    assert response.content_type == 'application/xml; charset=utf-8'

    # Compare just the verb part of the oai xml
    original, target = construct_oai_xml_comparisons(
        'tests/integration/fixtures/oai_getrecord_datacite.xml',
        response.get_data(),
        "GetRecord"
    )

    # Compare the main part of the request against test case
    assert original == target

def test_get_record_invalid_xml_datacite(client, mocker):
    """Test the getRecord verb responds and conforms as expected in datacite format with XML with invalid characters"""

    # Mock the datacite service to ensure the same record data is returned.
    mocked_get_metadata = mocker.patch('viringo.services.datacite.get_metadata')
    # Get fake result
    result = factories.InvalidXMLMetadataFactory()
    # Set the mocked service to use the fake result
    mocked_get_metadata.return_value = result

    response = client.get(
        '/oai?verb=GetRecord&metadataPrefix=datacite&identifier=doi:10.5072/not-a-real-doi'
    )

    assert response.status_code == 200
    assert response.content_type == 'application/xml; charset=utf-8'

    # Compare just the verb part of the oai xml
    original, target = construct_oai_xml_comparisons(
        'tests/integration/fixtures/oai_getrecord_datacite_invalid.xml',
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
        updated_datetime=datetime.datetime(2018, 5, 17, 6, 33),
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
    results = [result_1, result_2], 2, 1

    # Set the mocked service to use the fake result
    mocked_get_metadata_list.return_value = results

    response = client.get('/oai?verb=ListRecords&metadataPrefix=oai_dc&set=DATACITE.DATACITE')

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

def test_list_identifiers(client, mocker):
    """Test the listIdentifiers verb responds and conforms as expected"""

    # Mock the datacite service to ensure the same record data is returned.
    mocked_get_metadata_list = mocker.patch('viringo.services.datacite.get_metadata_list')

    # Get fake results
    result_1 = factories.MetadataFactory()
    result_2 = factories.MetadataFactory(
        identifier="10.5072/not-a-real-doi-2",
        updated_datetime=datetime.datetime(2018, 5, 17, 6, 33),
    )
    results = [result_1, result_2], 2, 1

    # Set the mocked service to use the fake result
    mocked_get_metadata_list.return_value = results

    response = client.get('/oai?verb=ListIdentifiers&metadataPrefix=oai_dc&set=DATACITE.DATACITE')

    assert response.status_code == 200
    assert response.content_type == 'application/xml; charset=utf-8'

    # Compare just the verb part of the oai xml
    original, target = construct_oai_xml_comparisons(
        'tests/integration/fixtures/oai_listidentifiers.xml',
        response.get_data(),
        "ListIdentifiers"
    )

    # Compare the main part of the request against test case
    assert original == target

def test_list_sets(client, mocker):
    """Test the listIdentifiers verb responds and conforms as expected"""

    # Mock the datacite service to ensure the same record data is returned.
    mocked_get_sets = mocker.patch('viringo.services.datacite.get_sets')

    # Get fake results
    results = [
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

    # Set the mocked service to use the fake result
    mocked_get_sets.return_value = results, len(results)

    response = client.get('/oai?verb=ListSets')

    assert response.status_code == 200
    assert response.content_type == 'application/xml; charset=utf-8'

    # Compare just the verb part of the oai xml
    original, target = construct_oai_xml_comparisons(
        'tests/integration/fixtures/oai_listsets.xml',
        response.get_data(),
        "ListSets"
    )

    # Compare the main part of the request against test case
    assert original == target

def test_list_metadata_formats(client):
    """Test the identify verb responds and conforms as expected"""
    response = client.get('/oai?verb=ListMetadataFormats')

    assert response.status_code == 200
    assert response.content_type == 'application/xml; charset=utf-8'

    # Compare just the verb part of the oai xml
    original, target = construct_oai_xml_comparisons(
        'tests/integration/fixtures/oai_listmetadataformats.xml',
        response.get_data(),
        "ListMetadataFormats"
    )

    # Compare the main part of the request against test case
    assert original == target

def test_responds_to_get_post(client):
    """Test OAI responds on both GET and POST method requests as per OAI spec"""
    response = client.get('/oai/')

    print(response.get_data())
    assert response.status_code == 200
    assert response.content_type == 'application/xml; charset=utf-8'

    response = client.post('/oai')

    assert response.status_code == 200
    assert response.content_type == 'application/xml; charset=utf-8'

OAI_NS = {'oai': 'http://www.openarchives.org/OAI/2.0/'}
UNPARSEABLE_XML = b'<resource><title>Unclosed</resource>'

def record_identifiers(response):
    """Return the identifiers of the records in an OAI response"""
    return etree.fromstring(response.get_data()).xpath(
        '//oai:record/oai:header/oai:identifier/text()', namespaces=OAI_NS
    )

@pytest.mark.parametrize('metadata_prefix', ['datacite', 'oai_datacite'])
def test_list_records_skips_unparseable_xml(client, mocker, caplog, metadata_prefix):
    """Test a record with XML that can't be parsed is skipped without failing the page"""

    mocked_get_metadata_list = mocker.patch('viringo.services.datacite.get_metadata_list')
    results = [
        factories.MetadataFactory(identifier='10.5072/good-1'),
        factories.MetadataFactory(identifier='10.5072/broken', xml=UNPARSEABLE_XML),
        factories.MetadataFactory(identifier='10.5072/good-2'),
    ]
    mocked_get_metadata_list.return_value = results, 3, 'next-page'

    response = client.get('/oai?verb=ListRecords&metadataPrefix=' + metadata_prefix)

    assert response.status_code == 200
    assert record_identifiers(response) == ['doi:10.5072/good-1', 'doi:10.5072/good-2']
    # Harvesters can still move on to the next page
    assert etree.fromstring(response.get_data()).find(
        './/oai:resumptionToken', namespaces=OAI_NS
    ).text
    assert 'Skipping doi:10.5072/broken' in caplog.text

@pytest.mark.parametrize('metadata_prefix', ['datacite', 'oai_datacite'])
def test_list_records_deleted_record_without_xml(client, mocker, metadata_prefix):
    """Test a deleted record with no stored XML is listed with only its header"""

    mocked_get_metadata_list = mocker.patch('viringo.services.datacite.get_metadata_list')
    deleted = factories.MetadataFactory(identifier='10.5072/deleted', xml=None, active=False)
    mocked_get_metadata_list.return_value = [deleted], 1, None

    response = client.get('/oai?verb=ListRecords&metadataPrefix=' + metadata_prefix)

    assert response.status_code == 200
    header = etree.fromstring(response.get_data()).find('.//oai:header', namespaces=OAI_NS)
    assert header.get('status') == 'deleted'

@pytest.mark.parametrize('metadata_prefix', ['datacite', 'oai_datacite'])
def test_get_record_unparseable_xml(client, mocker, caplog, metadata_prefix):
    """Test GetRecord for a record whose XML can't be parsed returns an OAI error"""

    mocked_get_metadata = mocker.patch('viringo.services.datacite.get_metadata')
    mocked_get_metadata.return_value = factories.MetadataFactory(
        identifier='10.5072/broken', xml=UNPARSEABLE_XML
    )

    response = client.get(
        '/oai?verb=GetRecord&metadataPrefix=%s&identifier=doi:10.5072/broken' % metadata_prefix
    )

    assert response.status_code == 200
    errors = etree.fromstring(response.get_data()).findall('.//oai:error', namespaces=OAI_NS)
    assert [e.get('code') for e in errors] == ['cannotDisseminateFormat']
    assert 'Unable to parse stored XML for doi:10.5072/broken' in caplog.text

def test_get_record_unparseable_xml_oai_dc(client, mocker):
    """Test a record whose XML can't be parsed is still served in oai_dc"""

    mocked_get_metadata = mocker.patch('viringo.services.datacite.get_metadata')
    mocked_get_metadata.return_value = factories.MetadataFactory(
        identifier='10.5072/broken', xml=UNPARSEABLE_XML
    )

    response = client.get(
        '/oai?verb=GetRecord&metadataPrefix=oai_dc&identifier=doi:10.5072/broken'
    )

    assert response.status_code == 200
    assert record_identifiers(response) == ['doi:10.5072/broken']
