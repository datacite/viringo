"""Tests for http endpoints of OAI-PMH verbs"""

from lxml import etree

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
        'tests/files/oai_identify.xml',
        response.get_data(),
        "Identify"
    )

    # Compare the main part of the request against test case
    assert original == target

def test_get_record_dc(client):
    """Test the getRecord verb responds and conforms as expected"""
    # Mock the datacite service to ensure the same record data is returned.

    response = client.get('/?verb=GetRecord&metadataPrefix=oai_dc&identifier=doi:10.5438/prvv-nv23')

    assert response.status_code == 200
    assert response.content_type == 'application/xml; charset=utf-8'

    # Compare just the verb part of the oai xml
    original, target = construct_oai_xml_comparisons(
        'tests/files/oai_getrecord_dc.xml',
        response.get_data(),
        "GetRecord"
    )
    print(original, target)

    # Compare the main part of the request against test case
    assert original == target
