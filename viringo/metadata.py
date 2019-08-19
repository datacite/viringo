"""This module deals with handling the representation of metadata formats for OAI"""

from lxml import etree

NS_OAIPMH = 'http://www.openarchives.org/OAI/2.0/'
NS_XSI = 'http://www.w3.org/2001/XMLSchema-instance'
NS_OAIDC = 'http://www.openarchives.org/OAI/2.0/oai_dc/'
NS_DC = "http://purl.org/dc/elements/1.1/"

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
            new_element = etree.SubElement(e_dc, nsdc(name))
            new_element.text = value

def datacite_writer(element: etree.Element, metadata):
    """Writer for writing data in a metadata object out into raw datacite format"""
    _map = metadata.getMap()
    raw_xml = _map.get('xml', '')

    xml_resource_element = etree.fromstring(raw_xml)

    element.append(xml_resource_element)