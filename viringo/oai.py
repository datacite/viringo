"""OAI-PMH main request handling"""

from xml.dom import minidom
from lxml.etree import ElementTree, Element, SubElement

from flask import (
    Blueprint, g, request, current_app
)
import oaipmh.common
import oaipmh.metadata
import oaipmh.server
import oaipmh.datestamp

from .catalogs import DataCiteOAIServer
from .catalogs import FRDROAIServer
from . import metadata
from . import config

BP = Blueprint('oai', __name__)

class XMLTreeServer(oaipmh.server.XMLTreeServer):
    def __init__(self, server, metadata_registry, nsmap=None):
        super(XMLTreeServer, self).__init__(
            server,
            metadata_registry,
            nsmap)

    def _outputResuming(self, element, input_func, output_func, kw):
        if 'resumptionToken' in kw:
            resumption_token = kw['resumptionToken']
            result, total_records, token = input_func(resumptionToken=resumption_token)
            # unpack keywords from resumption token
            token_kw, dummy = oaipmh.server.decodeResumptionToken(resumption_token)
        else:
            result, total_records, token = input_func(**kw)

            if not result:
                raise oaipmh.error.NoRecordsMatchError(
                    "No records match for request.")
            token_kw = kw
        output_func(element, result, token_kw)
        if token is not None:
            e_resumption_token = SubElement(element, '{%s}%s' % (metadata.NS_OAIPMH, 'resumptionToken'))
            e_resumption_token.text = token
            e_resumption_token.set('completeListSize', str(total_records))

class Server(oaipmh.server.ServerBase):
    """Expects to be initialized with a IOAI server implementation."""
    def __init__(self, server, metadata_registry=None, nsmap=None):
        resumption_server = Resumption(server)
        super(Server, self).__init__(
            resumption_server,
            metadata_registry,
            nsmap)
        # Override the XML tree writing server for some custom output
        self._tree_server = XMLTreeServer(resumption_server, metadata_registry, nsmap)

class Resumption(oaipmh.common.ResumptionOAIPMH):
    """ A custom resumption server based on the pyoai implementation
    This class exists because we have to handle resumption tokens ourselves to support
    arbitrary cursors that might be passed around i.e. custom cursor from an api.
    We handle this by allowing a paging_cursor to be specified as an additional kw arg.
    """
    def __init__(self, server):
        self._server = server

    def handleVerb(self, verb, kw):
        # Get the method that matches the verb we want to call.
        method = oaipmh.common.getMethodForVerb(self._server, verb)

        if 'resumptionToken' in kw:
            # Handling a resumption token, so work out arguments for next method
            kw, _ = oaipmh.server.decodeResumptionToken(kw['resumptionToken'])

        if verb in ['ListSets', 'ListIdentifiers', 'ListRecords']:
            # Call underlying method to get results
            result, total_records, resume_cursor = method(**kw)
            kw['paging_cursor'] = resume_cursor

            # When a cursor exists more results can be resumed, otherwise it's the end.
            if resume_cursor:
                # Always pass 1 as the underlying code expects something
                # and we handle our own pagination using our paging_cursor instead
                token = oaipmh.server.encodeResumptionToken(kw, cursor=1)
            else:
                token = "" # Provide a blank token as per oaipmh spec

            # With paging verbs return a token
            return result, total_records, token
        else:
            # Call underlying method to get results
            result = method(**kw)
            return result

def get_oai_server():
    """Returns a pyoai server object that can process and return OAI requests"""
    if 'oai' not in g:
        if config.CATALOG_SET == 'DateCite':
            catalog_server = DataCiteOAIServer()
        elif config.CATALOG_SET == 'FRDR':
            catalog_server = FRDROAIServer()
        else:
            print('No valid metadata catalog configured')
            sys.exit(1)

        metadata_registry = oaipmh.metadata.MetadataRegistry()
        metadata_registry.registerWriter('oai_dc', metadata.oai_dc_writer)
        metadata_registry.registerWriter('oai_datacite', metadata.oai_datacite_writer)
        metadata_registry.registerWriter('datacite', metadata.datacite_writer)
        oai = Server(catalog_server, metadata_registry)

        g.oai = oai

    return g.oai

@BP.route('/', methods=['GET', 'POST'])
def index():
    """Root OAIPMH request handler"""

    # Params
    oai_request_args = {}
    oai_request_args['verb'] = request.args.get('verb', 'Identify')

    if request.args.get('metadataPrefix'):
        oai_request_args['metadataPrefix'] = request.args.get('metadataPrefix')

    if request.args.get('identifier'):
        oai_request_args['identifier'] = request.args.get('identifier')

    if request.args.get('resumptionToken'):
        oai_request_args['resumptionToken'] = request.args.get('resumptionToken')

    if request.args.get('set'):
        oai_request_args['set'] = request.args.get('set')

    if request.args.get('from'):
        oai_request_args['from'] = request.args.get('from')

    if request.args.get('until'):
        oai_request_args['until'] = request.args.get('until')

    current_app.logger.info("OAI request %s", oai_request_args['verb'], extra=oai_request_args)

    # Obtain a OAI-PMH server interface to handle requests
    oai = get_oai_server()

    # Handle a request for a specific verb
    xml = oai.handleRequest(oai_request_args)

    # This isn't the prettiest way but we need to add the xsl stylesheet
    dom = minidom.parseString(xml)
    process_instruction = dom.createProcessingInstruction(
        'xml-stylesheet',
        'type="text/xsl" href="/static/oaitohtml.xsl"'
    )
    root = dom.firstChild
    dom.insertBefore(process_instruction, root)
    xml = dom.toxml()

    return xml
