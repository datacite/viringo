"""Script for running WSGI process"""

import sys
import logging
import json_log_formatter

from viringo import create_app

application = create_app()

if not application.debug:
    formatter = json_log_formatter.JSONFormatter()
    json_handler = logging.StreamHandler(sys.stdout)
    json_handler.setFormatter(formatter)

    # Set the only handler to be our JSON stdout handler
    logger = logging.getLogger()
    logger.handlers = [json_handler]
