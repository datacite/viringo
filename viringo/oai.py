"""OAI-PMH main request handling"""

from flask import (
    Blueprint, g, request
)
from oaipmh import server, metadata
from .catalogs import DataCiteOAIServer

BP = Blueprint('oai', __name__)

from lxml.etree import ElementTree, Element, SubElement
from lxml import etree

NS_OAIPMH = 'http://www.openarchives.org/OAI/2.0/'
NS_XSI = 'http://www.w3.org/2001/XMLSchema-instance'
NS_OAIDC = 'http://www.openarchives.org/OAI/2.0/oai_dc/'
NS_DC = "http://purl.org/dc/elements/1.1/"

def oai_dc_writer(element, metadata):
    def nsoai(name):
        return '{%s}%s' % (NS_OAIPMH, name)

    def nsoaidc(name):
        return '{%s}%s' % (NS_OAIDC, name)

    def nsdc(name):
        return '{%s}%s' % (NS_DC, name)

    e_dc = SubElement(element, nsoaidc('dc'),
                      nsmap={'oai_dc': NS_OAIDC, 'dc': NS_DC, 'xsi': NS_XSI})
    e_dc.set('{%s}schemaLocation' % NS_XSI,
             '%s http://www.openarchives.org/OAI/2.0/oai_dc.xsd' % NS_OAIDC)
    map = metadata.getMap()
    for name in [
        'title', 'creator', 'publisher', 'publicationYear',
        'date', 'identifier', 'relation', 'subject', 'description', 'contributor',
        'language', 'type', 'format', 'source', 'rights']:
        for value in map.get(name, []):
            e = SubElement(e_dc, nsdc(name))
            e.text = value

def get_oai_server():
    """Returns a server that can process and return OAI requests"""
    if 'oai' not in g:
        catalog_server = DataCiteOAIServer()

        metadata_registry = metadata.MetadataRegistry()
        metadata_registry.registerWriter('oai_dc', oai_dc_writer)
        oai = server.Server(catalog_server,
                            metadata_registry,
                            resumption_batch_size=7)

        g.oai = oai

    return g.oai

@BP.route('/')
def index():
    """Root OAIPMH request handler"""

    # Params
    oai_request_args = {}
    oai_request_args['verb'] = request.args.get('verb', 'Identify')

    if request.args.get('metadataPrefix'):
        oai_request_args['metadataPrefix'] = request.args.get('metadataPrefix')

    if request.args.get('identifier'):
        oai_request_args['identifier'] = request.args.get('identifier')

    # Obtain a OAI-PMH server interface to handle requests
    oai = get_oai_server()

    # Handle a request for a specific verb
    xml = oai.handleRequest(oai_request_args)

    return xml
