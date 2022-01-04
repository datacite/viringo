"""This module deals with handling the representation of metadata formats for OAI"""

import re
import ftfy
from lxml import etree

NS_OAIPMH = 'http://www.openarchives.org/OAI/2.0/'
NS_XSI = 'http://www.w3.org/2001/XMLSchema-instance'
NS_OAIDC = 'http://www.openarchives.org/OAI/2.0/oai_dc/'
NS_DC = "http://purl.org/dc/elements/1.1/"
OAI_DATACITE_NS = "http://schema.datacite.org/oai/oai-1.1/"

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
                if isinstance(value, list):
                    if len(value) == 1:
                        value = value[0]
                    else:
                        value = str(value)
                new_element = etree.SubElement(e_dc, nsdc(name))
                if isinstance(value, str):
                    try:
                        value = value.replace('\x0c', " ")
                        new_element.text = ftfy.fix_text(value)
                    except:
                        new_element.text = ''
                else:
                    new_element.text = ''

def datacite_writer(element: etree.Element, metadata):
    """Writer for writing data in a metadata object out into raw datacite format"""
    _map = metadata.getMap()
    raw_xml = _map.get('xml', '')

    xml_resource_element = etree.fromstring(raw_xml)

    element.append(xml_resource_element)

def oai_datacite_writer(element: etree.Element, metadata):
    """Writer for writing data in a metadata object out into raw datacite format"""
    _map = metadata.getMap()
    raw_xml = _map.get('xml', '')

    try:
        xml_resource_element = etree.fromstring(raw_xml)
    except:
        print(raw_xml)

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
