"""OAI-PMH http server repository implementation"""
import os

from flask import Flask, Response

class DefaultResponse(Response):
    default_mimetype = 'application/xml'

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY='dev',
    )

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
    app.register_blueprint(oai.bp)

    # We want to use a custom response object for default content types
    app.response_class = DefaultResponse

    return app
