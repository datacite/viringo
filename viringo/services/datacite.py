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
    published_date = ''
    contributor = ''
    resource_type = ''
    formats = []
    identifiers = []
    language = ''
    relations = []
    rights = []
    client = ''


def related_identifier_to_string(related_identifier):
    """Take a related identifier and return in a formatted single string"""
    _id = related_identifier.get('relatedIdentifier')
    _type = related_identifier.get('relatedIdentifierType') or ''
    return _type.lower() + ":" + _id

def identifier_to_string(identifier):
    """Take an identifier and return in a formatted in single string"""
    _id = identifier.get('identifier')
    _type = identifier.get('identifierType') or ''
    return _type.lower() + ":" + _id

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
    result.published_date = data['attributes'].get('published') or ''
    result.contributor = data['attributes'].get('contributor') or ''
    result.resource_type = data['attributes']['types'].get('resourceTypeGeneral') or ''
    result.formats = data['attributes'].get('formats') or []
    result.identifiers = result.relations = [
        identifier_to_string(identifier) for identifier in data['attributes']['identifiers']
    ]
    result.language = data['attributes'].get('language') or ''
    result.relations = [
        related_identifier_to_string(relation)
        for relation in data['attributes']['relatedIdentifiers']
    ]
    result.rights = [right.get('rights', '') for right in data['attributes']['rightsList']]

    result.client = data['relationships']['client']['data'].get('id') or ''

    return result

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
