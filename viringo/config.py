"""Configuration"""

import os

# Sentry DSN
SENTRY_DSN = os.getenv('SENTRY_DSN', None)
# URL used for the DataCite REST API
DATACITE_API_URL = os.getenv('DATACITE_API_URL', 'https://api.test.datacite.org')
# Admin credentials for the API
API_ADMIN_USERNAME = os.getenv('API_ADMIN_USERNAME')
API_ADMIN_PASSWORD = os.getenv('API_ADMIN_PASSWORD')

# Name used to identifier the repository.
OAIPMH_REPOS_NAME = os.getenv('OAIPMH_REPOS_NAME', 'DataCite')
# Base URL reported for where the OAI-PMH service is hosted
OAIPMH_BASE_URL = os.getenv('OAIPMH_BASE_URL', 'https://oai.datacite.org/oai')
# Admin e-mail for the OAI-PMH service
OAIPMH_ADMIN_EMAIL = os.getenv('OAIPMH_ADMIN_EMAIL', 'support@datacite.org')
# OAI repository identifier
OAIPMH_IDENTIFIER = os.getenv('OAIPMH_IDENTIFIER', 'oai.datacite.org')
# Page size of results shown for result listings
RESULT_SET_SIZE = int(os.getenv('RESULT_SET_SIZE', '50'))
# Source metadata catalog (DataCite or FRDR)
CATALOG_SET = os.getenv('OAIPMH_CATALOG', 'DataCite')
# FRDR Postgres server
POSTGRES_SERVER = os.getenv('OAIPMH_POSTGRES_SERVER', '')
# FRDR Postgres db
POSTGRES_DB = os.getenv('OAIPMH_POSTGRES_DB', '')
# FRDR Postgres user
POSTGRES_USER = os.getenv('OAIPMH_POSTGRES_USER', '')
# FRDR Postgres password
POSTGRES_PASSWORD = os.getenv('OAIPMH_POSTGRES_PASSWORD', '')