"""Configuration"""

import os

# Sentry DSN
SENTRY_DSN = os.getenv('SENTRY_DSN', None)
# URL used for the DataCite REST API
DATACITE_API_URL = os.getenv('DATACITE_API_URL', 'https://api.datacite.org')
# Admin credentials for the API
DATACITE_API_ADMIN_USERNAME = os.getenv('DATACITE_API_ADMIN_USERNAME', 'admin')
DATACITE_API_ADMIN_PASSWORD = os.getenv('DATACITE_API_ADMIN_PASSWORD')

# Name used to identifier the repository.
OAIPMH_REPOS_NAME = os.getenv('OAIPMH_REPOS_NAME', 'DataCite')
# Base URL reported for where the OAI-PMH service is hosted
OAIPMH_BASE_URL = os.getenv('OAIPMH_BASE_URL', 'https://oai.datacite.org/oai')
# Admin e-mail for the OAI-PMH service
OAIPMH_ADMIN_EMAIL = os.getenv('OAIPMH_ADMIN_EMAIL', 'support@datacite.org')
# Page size of results shown for result listings
RESULT_SET_SIZE = int(os.getenv('RESULT_SET_SIZE', '50'))
