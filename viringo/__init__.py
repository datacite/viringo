"""OAI-PMH http server repository implementation"""
import os
from flask import Flask, Response, redirect, url_for
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from . import config

sentry_sdk.init(
    dsn=config.SENTRY_DSN,
    integrations=[FlaskIntegration()]
)

class DefaultResponse(Response):
    """Handles default responses for the OAI-PMH responses"""
    default_mimetype = 'application/xml'

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping()
    app.url_map.strict_slashes = False

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register Blueprints
    from viringo import oai
    app.register_blueprint(oai.BP, url_prefix="/oai")

    @app.route('/')
    def index():
        return redirect(url_for('oai.index'))

    # Register heartbeat
    @app.route('/heartbeat')
    def heartbeat():
        """General healthcheck route"""
        resp = Response(response='OK',
                        status=200,
                        mimetype="text/plain")
        return resp

    # We want to use a custom response object for default content types
    app.response_class = DefaultResponse

    return app
