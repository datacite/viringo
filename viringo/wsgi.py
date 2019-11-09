"""Script for running WSGI process"""

import os
import sys
import logging
from logstash_formatter import LogstashFormatterV1
from dotenv import load_dotenv

from viringo import create_app

# load env variables from .env file
load_dotenv()

application = create_app()

# Configure logging
stdout_handler = logging.StreamHandler(sys.stdout)

# Use JSON stdout handler if not in debug mode
if not application.debug:
    formatter = LogstashFormatterV1()
    stdout_handler.setFormatter(formatter)

logger = logging.getLogger('werkzeug')
logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))
logger.handlers = [stdout_handler]
