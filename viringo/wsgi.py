"""Script for running WSGI process"""

import os
import sys
import logging
import json_log_formatter
from dotenv import load_dotenv

from viringo import create_app

load_dotenv()

application = create_app()

# Configure logging
stdout_handler = logging.StreamHandler(sys.stdout)

# Use JSON stdout handler if not in debug mode
if not application.debug:
    formatter = json_log_formatter.JSONFormatter()
    stdout_handler.setFormatter(formatter)

logger = logging.getLogger('werkzeug')
logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))
logger.handlers = [stdout_handler]
