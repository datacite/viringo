"""Handles interactions to the DataCite REST Service for retrieving metadata"""

import base64
from datetime import datetime
import dateutil.parser
import dateutil.tz

import requests

class DataCiteResult:
    """Represents a DataCite metadata resultset"""
    created_datetime: datetime = datetime.min
    xml = ''
    titles = []
    creators = []
    subjects = []
    descriptions = []
    publisher = ''
    publication_year = ''
    dates = []
    contributors = []
    resource_types = []
    funding_references = []
    geo_locations = []
    formats = []
    identifiers = []
    language = ''
    relations = []
    rights = []
    sizes = []
    client = ''

def build_result(data):
    """Parse single json-api data dict into service result object"""
    result = DataCiteResult()
    # Here we want to parse a ISO date but convert to UTC and then remove the TZinfo entirely
    # This is because OAI always works in UTC.
    updated = dateutil.parser.parse(data['attributes']['updated'])
    result.created_datetime = updated.astimezone(dateutil.tz.UTC).replace(tzinfo=None)

    result.xml = base64.b64decode(data['attributes']['xml'])
    result.titles = [title.get('title', '') for title in data['attributes']['titles']]
    result.creators = [creator.get('name', '') for creator in data['attributes']['creators']]
    result.subjects = [subject.get('subject', '') for subject in data['attributes']['subjects']]
    result.descriptions = [
        description.get('description', '') for description in data['attributes']['descriptions']
    ]
    result.publisher = data['attributes'].get('publisher') or ''
    result.publication_year = data['attributes'].get('publicationYear') or ''
    result.dates = [
        {'type': date['dateType'], 'date': date['date']} for date in data['attributes']['dates']
    ]
    result.contributors = data['attributes'].get('contributors') or []
    result.funding_references = data['attributes'].get('fundingReferences') or []
    result.sizes = data['attributes'].get('sizes') or []
    result.geo_locations = data['attributes'].get('geoLocations') or []
    result.resource_types = [
        data['attributes']['types'].get('resourceTypeGeneral') or '',
        data['attributes']['types'].get('resourceType') or ''
    ]
    result.formats = data['attributes'].get('formats') or []
    result.identifiers = [
        {'type': identifier['identifierType'], 'identifier': strip_uri_prefix(identifier['identifier']).upper()}
        for identifier in data['attributes']['identifiers']
    ]
    result.language = data['attributes'].get('language') or ''
    result.relations = [
        {'type': related['relatedIdentifierType'], 'identifier': related['relatedIdentifier']}
        for related in data['attributes']['relatedIdentifiers']
    ]
    result.rights = [{'statement': right['rights'], 'uri': right['rightsUri']} for right in data['attributes']['rightsList']]
    result.client = data['relationships']['client']['data'].get('id').upper() or ''

    return result

def strip_uri_prefix(identifier):
    """Strip common prefixes because OAI doesn't work with those kind of ID's"""
    if identifier.startswith("https://doi.org/"):
        _, identifier = identifier.split("https://doi.org/")
    return identifier

def get_metadata(doi):
    """Return a parsed metadata result from the dataset API

    Aside from the raw xml, the attributes parsed are best guesses for returning filled data.
    """
    api_url = 'http://api.datacite.org'
    response = requests.get(api_url + '/dois/' + doi)
    if response.status_code == 200:
        data = response.json()['data']
        return build_result(data)
    else:
        return None
