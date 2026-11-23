"""Unit tests for parsing raw DataCite XML"""

import pytest
from lxml import etree

from viringo import metadata

def resource_xml(title, encoding='UTF-8'):
    """Builds a minimal resource document encoded as declared"""
    return (
        f'<?xml version="1.0" encoding="{encoding}"?>'
        f'<resource><title>{title}</title></resource>'
    ).encode(encoding)

def title_of(element):
    """Returns the text of the title element"""
    return element.findtext('title')

def test_parse_datacite_xml_valid_utf8():
    """Valid UTF-8 XML is parsed unchanged"""
    element = metadata.parse_datacite_xml(resource_xml('Résumé'))
    assert title_of(element) == 'Résumé'

@pytest.mark.parametrize('encoding', ['ISO-8859-1', 'UTF-16'])
def test_parse_datacite_xml_honours_declared_encoding(encoding):
    """Valid XML in a non-UTF-8 encoding is decoded using its declaration"""
    element = metadata.parse_datacite_xml(resource_xml('Résumé', encoding))
    assert title_of(element) == 'Résumé'

def test_parse_datacite_xml_strips_invalid_characters():
    """UTF-8 XML containing characters not allowed in XML is cleaned and parsed"""
    element = metadata.parse_datacite_xml(resource_xml('Résumé pass\u0002through\u001f'))
    assert title_of(element) == 'Résumé passthrough'

def test_parse_datacite_xml_reraises_when_not_fixable():
    """XML that is broken for another reason still raises a syntax error"""
    with pytest.raises(etree.XMLSyntaxError):
        metadata.parse_datacite_xml(b'<resource><title>Unclosed</resource>')

def test_parse_datacite_xml_reraises_for_non_utf8_with_invalid_characters():
    """Non-UTF-8 XML with invalid characters is not guessed at"""
    with pytest.raises(etree.XMLSyntaxError):
        metadata.parse_datacite_xml(resource_xml('Résumé\u0002', 'ISO-8859-1'))

def test_parse_datacite_xml_reraises_for_declared_non_utf8_that_decodes_as_utf8():
    """A declared non-UTF-8 encoding is respected even if its bytes are valid UTF-8"""
    raw_xml = resource_xml('日本\u0002', 'ISO-2022-JP')
    raw_xml.decode('utf-8')  # ISO-2022-JP is 7-bit, so it is also valid UTF-8

    with pytest.raises(etree.XMLSyntaxError):
        metadata.parse_datacite_xml(raw_xml)

@pytest.mark.parametrize('raw_xml', [
    b'\xef\xbb\xbf<?xml version="1.0" encoding="UTF-8"?><resource><title>a\x02b</title></resource>',
    b"<?xml version='1.0' encoding='utf-8'?><resource><title>a\x02b</title></resource>",
    b'<resource><title>a\x02b</title></resource>',
])
def test_parse_datacite_xml_strips_invalid_characters_for_utf8_forms(raw_xml):
    """UTF-8 is recognised with a BOM, a lowercase declaration or no declaration"""
    assert title_of(metadata.parse_datacite_xml(raw_xml)) == 'ab'
