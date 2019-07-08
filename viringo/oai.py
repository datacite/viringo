"""OAI-PMH main request handling"""

from flask import (
    Blueprint, g, request
)
import oaipmh.metadata
import oaipmh.server
from .catalogs import DataCiteOAIServer
from . import metadata

BP = Blueprint('oai', __name__)

def get_oai_server():
    """Returns a server that can process and return OAI requests"""
    if 'oai' not in g:
        catalog_server = DataCiteOAIServer()

        metadata_registry = oaipmh.metadata.MetadataRegistry()
        metadata_registry.registerWriter('oai_dc', metadata.oai_dc_writer)
        oai = oaipmh.server.Server(catalog_server,
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
