"""OAI-PMH main request handling"""

from flask import (
    Blueprint, g, request
)
import oaipmh.common
import oaipmh.metadata
import oaipmh.server
import oaipmh.datestamp

from .catalogs import DataCiteOAIServer
from . import metadata

BP = Blueprint('oai', __name__)


class Server(oaipmh.server.ServerBase):
    """Expects to be initialized with a IOAI server implementation."""
    def __init__(self, server, metadata_registry=None, nsmap=None):
        super(Server, self).__init__(
            Resumption(server),
            metadata_registry,
            nsmap)

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
            result, resume_cursor = method(**kw)
            kw['paging_cursor'] = resume_cursor

            # When a cursor exists more results can be resumed, otherwise it's the end.
            if resume_cursor:
                # Always pass 1 as the cursor because we handle cursor
                # navigation via the paging_cursor
                token = oaipmh.server.encodeResumptionToken(kw, cursor=None)
            else:
                token = "" # Provide a blank token as per oaipmh spec

            # With paging verbs return a token
            return result, token
        else:
            # Call underlying method to get results
            result = method(**kw)
            return result

def get_oai_server():
    """Returns a pyoai server object that can process and return OAI requests"""
    if 'oai' not in g:
        catalog_server = DataCiteOAIServer()

        metadata_registry = oaipmh.metadata.MetadataRegistry()
        metadata_registry.registerWriter('oai_dc', metadata.oai_dc_writer)
        oai = Server(catalog_server, metadata_registry)

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

    if request.args.get('resumptionToken'):
        oai_request_args['resumptionToken'] = request.args.get('resumptionToken')

    if request.args.get('set'):
        oai_request_args['set'] = request.args.get('set')

    if request.args.get('from'):
        oai_request_args['from'] = request.args.get('from')

    if request.args.get('until'):
        oai_request_args['until'] = request.args.get('until')

    # Obtain a OAI-PMH server interface to handle requests
    oai = get_oai_server()

    # Handle a request for a specific verb
    xml = oai.handleRequest(oai_request_args)

    return xml
