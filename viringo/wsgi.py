"""Script for running WSGI process"""

import os
import sys
import logging
import json_log_formatter
from dotenv import load_dotenv

from viringo import create_app

# load env variables from .env file
load_dotenv()

application = create_app()

from flask.logging import default_handler

logger = application.logger
if not logger.handlers:
    stdout_handler = logging.StreamHandler(sys.stdout)

    logger.removeHandler(default_handler)

    formatter = json_log_formatter.JSONFormatter()
    stdout_handler.setFormatter(formatter)

    logger.handlers = [stdout_handler]
    logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))

