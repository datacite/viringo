"""This module deals with handling the representation of metadata formats for OAI"""

import re
from lxml import etree

NS_OAIPMH = 'http://www.openarchives.org/OAI/2.0/'
NS_XSI = 'http://www.w3.org/2001/XMLSchema-instance'
NS_OAIDC = 'http://www.openarchives.org/OAI/2.0/oai_dc/'
NS_DC = "http://purl.org/dc/elements/1.1/"
OAI_DATACITE_NS = "http://schema.datacite.org/oai/oai-1.1/"

# Matches runs of characters that XML 1.0 does not allow:
# Char ::= #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF]
INVALID_XML_CHARS = re.compile(
    '[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\U00010000-\U0010FFFF]+'
)

def strip_invalid_xml_chars(value: str) -> str:
    """Remove characters that are not allowed in an XML 1.0 document"""
    return INVALID_XML_CHARS.sub('', value)

# The encoding named in an XML declaration, which must open the document
XML_DECLARED_ENCODING = re.compile(
    rb'(?:\xef\xbb\xbf)?<\?xml[^>]*?\sencoding\s*=\s*["\']([^"\']+)["\']'
)

def is_utf8_xml(raw_xml: bytes) -> bool:
    """Whether a document is UTF-8, either by declaration or by default"""
    declaration = XML_DECLARED_ENCODING.match(raw_xml)
    if declaration and declaration.group(1).lower() not in (b'utf-8', b'utf8'):
        return False

    try:
        raw_xml.decode('utf-8')
    except UnicodeDecodeError:
        return False

    return True

def parse_datacite_xml(raw_xml: bytes) -> etree._Element:
    """Parse raw DataCite XML into an element.

    The original bytes are parsed first so lxml honours the document's declared
    encoding. Only if that fails, UTF-8 documents are retried with characters
    that are invalid in XML removed. Anything else re-raises the original error.
    """
    try:
        return etree.fromstring(raw_xml)
    except etree.XMLSyntaxError:
        if not is_utf8_xml(raw_xml):
            raise

        text = raw_xml.decode('utf-8')
        cleaned = strip_invalid_xml_chars(text)
        if cleaned == text:
            raise

        return etree.fromstring(cleaned.encode('utf-8'))

def oai_dc_writer(element: etree.Element, metadata):
    """Writer for writing data in a metadata object out into DC format"""

    def nsoaidc(name):
        return '{%s}%s' % (NS_OAIDC, name)

    def nsdc(name):
        return '{%s}%s' % (NS_DC, name)

    e_dc = etree.SubElement(element, nsoaidc('dc'),
                            nsmap={'dc': NS_DC, 'oai_dc': NS_OAIDC, 'xsi': NS_XSI})
    e_dc.set('{%s}schemaLocation' % NS_XSI,
             '%s http://www.openarchives.org/OAI/2.0/oai_dc.xsd' % NS_OAIDC)

    _map = metadata.getMap()
    for name in [
            'title',
            'creator',
            'publisher',
            'publicationYear',
            'date',
            'identifier',
            'relation',
            'subject',
            'description',
            'contributor',
            'language',
            'type',
            'format',
            'source',
            'rights'
        ]:
        for value in _map.get(name, []):
            if value:
                new_element = etree.SubElement(e_dc, nsdc(name))
                new_element.text = strip_invalid_xml_chars(value)

def datacite_writer(element: etree.Element, metadata):
    """Writer for writing data in a metadata object out into raw datacite format"""
    _map = metadata.getMap()

    xml_resource_element = parse_datacite_xml(_map.get('xml', b''))

    element.append(xml_resource_element)

def oai_datacite_writer(element: etree.Element, metadata):
    """Writer for writing data in a metadata object out into raw datacite format"""
    _map = metadata.getMap()

    xml_resource_element = parse_datacite_xml(_map.get('xml', b''))

    e_oai_datacite = etree.SubElement(
        element, "oai_datacite", {'xmlns': 'http://schema.datacite.org/oai/oai-1.1/'},
        nsmap={'xsi': NS_XSI}
    )

    e_oai_datacite.set(
        '{%s}schemaLocation' % NS_XSI, 'http://schema.datacite.org/oai/oai-1.1/ http://schema.datacite.org/oai/oai-1.1/oai.xsd'
    )

    schema_version = _map.get('metadata_version', '')

    e_schema_version = etree.SubElement(e_oai_datacite, 'schemaVersion')
    e_schema_version.text = str(schema_version)
    e_symbol = etree.SubElement(e_oai_datacite, 'datacentreSymbol')
    e_symbol.text = _map.get('set', '')

    e_payload = etree.SubElement(e_oai_datacite, 'payload')

    e_payload.append(xml_resource_element)
