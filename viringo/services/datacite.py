"""Handles interactions to the DataCite REST Service for retrieving metadata"""

import base64
import logging
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from operator import itemgetter
import dateutil.parser
import dateutil.tz
import requests
from viringo import config


class Metadata:
    """Represents a DataCite metadata resultset"""

    def __init__(
        self,
        identifier=None,
        created_datetime=None,
        updated_datetime=None,
        xml=None,
        metadata_version=None,
        titles=None,
        creators=None,
        subjects=None,
        descriptions=None,
        publisher=None,
        publication_year=None,
        dates=None,
        contributors=None,
        resource_types=None,
        funding_references=None,
        geo_locations=None,
        formats=None,
        identifiers=None,
        language=None,
        relations=None,
        rights=None,
        sizes=None,
        client=None,
        provider=None,
        active=True
    ):

        self.identifier = identifier
        self.created_datetime = created_datetime or datetime.min
        self.updated_datetime = updated_datetime or datetime.min
        self.xml = xml
        self.metadata_version = metadata_version
        self.titles = titles or []
        self.creators = creators or []
        self.subjects = subjects or []
        self.descriptions = descriptions or []
        self.publisher = publisher
        self.publication_year = publication_year
        self.dates = dates or []
        self.contributors = contributors or []
        self.resource_types = resource_types or []
        self.funding_references = funding_references or []
        self.geo_locations = geo_locations or []
        self.formats = formats or []
        self.identifiers = identifiers or []
        self.language = language
        self.relations = relations or []
        self.rights = rights or []
        self.sizes = sizes or []
        self.client = client
        self.provider = provider
        self.active = active


def build_metadata(data):
    """Parse single json-api data dict into metadata object"""
    result = Metadata()

    result.identifier = data.get('id')

    # Here we want to parse a ISO date but convert to UTC and then remove the TZinfo entirely
    # This is because OAI always works in UTC.
    created = dateutil.parser.parse(data['attributes']['created'])
    result.created_datetime = created.astimezone(
        dateutil.tz.UTC).replace(tzinfo=None)
    updated = dateutil.parser.parse(data['attributes']['updated'])
    result.updated_datetime = updated.astimezone(
        dateutil.tz.UTC).replace(tzinfo=None)

    result.xml = base64.b64decode(data['attributes']['xml']) \
        if data['attributes']['xml'] is not None else None

    result.metadata_version = data['attributes']['metadataVersion'] \
        if data['attributes']['metadataVersion'] is not None else None

    result.titles = [
        title.get('title', '') for title in data['attributes']['titles']
    ] if data['attributes']['titles'] is not None else []

    result.creators = [
        creator.get('name', '') for creator in data['attributes']['creators']
    ] if data['attributes']['creators'] is not None else []

    result.subjects = [
        subject.get('subject', '') for subject in data['attributes']['subjects']
    ] if data['attributes']['subjects'] is not None else []

    result.descriptions = [
        description.get('description', '') for description in data['attributes']['descriptions']
    ] if data['attributes']['descriptions'] is not None else []

    result.publisher = data['attributes'].get('publisher') or ''
    result.publication_year = data['attributes'].get('publicationYear') or ''

    result.dates = []
    if data['attributes']['dates'] is not None:
        for date in data['attributes']['dates']:
            if 'date' in date and 'dateType' in date:
                result.dates.append(
                    {'type': date['dateType'], 'date': date['date']})

    result.contributors = data['attributes'].get('contributors') or []
    result.funding_references = data['attributes'].get(
        'fundingReferences') or []
    result.sizes = data['attributes'].get('sizes') or []
    result.geo_locations = data['attributes'].get('geoLocations') or []

    result.resource_types = []
    result.resource_types += [data['attributes']['types'].get('resourceTypeGeneral')] \
        if data['attributes']['types'].get('resourceTypeGeneral') is not None else []
    result.resource_types += [data['attributes']['types'].get('resourceType')] \
        if data['attributes']['types'].get('resourceType') is not None else []

    result.formats = data['attributes'].get('formats') or []

    result.identifiers = []

    # handle missing identifiers attribute
    if data['attributes']['identifiers'] is not None:
        for identifier in data['attributes']['identifiers']:
            if identifier['identifier']:
                # Special handling for the fact the API could return bad identifier
                # as a list rather than a string
                if isinstance(identifier['identifier'], list):
                    identifier['identifier'] = ','.join(
                        identifier['identifier'])

                result.identifiers.append({
                    'type': identifier['identifierType'],
                    'identifier': strip_uri_prefix(identifier['identifier'])
                })

    result.language = data['attributes'].get('language') or ''

    result.relations = []
    if data['attributes']['relatedIdentifiers'] is not None:
        for related in data['attributes']['relatedIdentifiers']:
            if 'relatedIdentifier' in related:
                result.relations.append({
                    'type': related['relatedIdentifierType'],
                    'identifier': related['relatedIdentifier']
                })

    result.rights = [
        {'statement': right.get('rights', None),
         'uri': right.get('rightsUri', None)}
        for right in data['attributes']['rightsList']
    ] if data['attributes']['rightsList'] is not None else []

    result.client = data['relationships']['client']['data'].get(
        'id').upper() or ''

    result.provider = data['relationships']['provider']['data'].get(
        'id').upper() or ''

    # We make the active decision based upon if there is metadata and the isActive flag
    # This is the same as the previous oai-pmh datacite implementation.
    result.active = True if result.xml and data['attributes'].get(
        'isActive', True) else False

    return result


def strip_uri_prefix(identifier):
    """Strip common prefixes because OAI doesn't work with those kind of ID's"""
    if identifier and isinstance(identifier, str):
        if identifier.startswith("https://doi.org/"):
            _, identifier = identifier.split("https://doi.org/", 1)
    else:
        identifier = str(identifier)
    return identifier


def get_metadata(doi):
    """Return a parsed metadata result from the DataCite API

    Aside from the raw xml, the attributes parsed are best guesses for returning filled data.
    """

    response = api_call_get(config.DATACITE_API_URL + '/dois/' + doi, None)

    if response.status_code == 200:
        data = response.json()['data']
        return build_metadata(data)
    elif response.status_code == 404:
        return None
    else:
        logging.error("Error receiving data from datacite REST API")

    return None


def get_metadata_list(
    query=None,
    provider_id=None,
    client_id=None,
    from_datetime=None,
    until_datetime=None,
    cursor=None
):
    """Returns metadata in parsed metadata result from the DataCite API"""

    # Trigger cursor navigation with a starting value
    if not cursor:
        cursor = 1

    # Whenever just a from is specified always set the until to latest timestamp.
    if from_datetime and not until_datetime:
        until_datetime = datetime.now()

    # Construct a custom query for datetime filtering.
    # We use the updated date not the created date because users tend to prefer
    # seeing latest changes.
    datetime_query = ''
    if from_datetime and until_datetime:
        datetime_query = "updated:[{0}+TO+{1}]".format(
            from_datetime.isoformat(), until_datetime.isoformat()
        )

    params = {
        'detail': True,
        'page[size]': config.RESULT_SET_SIZE,
        'page[cursor]': cursor
    }

    # Only use the provider id if we dont have a client id
    # Otherwise just send client_id
    if not client_id:
        params['provider_id'] = provider_id
    else:
        params['client_id'] = client_id

    if datetime_query:
        if query:
            query = query + " AND " + datetime_query
        else:
            query = datetime_query

    if query:
        params['query'] = query

    url = config.DATACITE_API_URL + '/dois'

    json, cursor = api_get_cursor(url, params)

    # handle response that is not dict
    if type(json) is not dict:
        logging.debug('Response: %s', json)
        json = {'data': []}

    total_records = 0
    if 'meta' in json:
        total_records = json['meta']['total']

    data = json['data']
    results = []
    for doi_entry in data:
        result = build_metadata(doi_entry)
        results.append(result)

    return results, total_records, cursor


def get_sets():
    """Returns sets that can be used for further sub dividing results"""

    next_url = config.DATACITE_API_URL + '/clients'

    results = []

    while next_url:
        params = {
            'include': 'provider',
            'page[size]': 1000,
        }

        json, next_url = api_get_paging_with_url(next_url, params)

        if json:
            data = json['data']  # clients
            included = json['included']  # providers

            for entry in data:
                if entry['id'] not in results:
                    results.append((entry['id'], entry['attributes']['name']))

            for entry in included:
                if entry['id'] not in results:
                    results.append((entry['id'], entry['attributes']['name']))

    # Sort the results, this should be relativly fast given sets tend to be a small subset.
    results.sort(key=itemgetter(0))
    total_results = len(results)

    return results, total_results


def api_get_cursor(url, params):
    """Call the API expecting to page through with cursors"""

    response = api_call_get(url, params)

    if response.status_code == 200:
        json = response.json()

        if json['meta']['total'] == 0:
            return None, None

        # Grab out the cursor bit from the full next link
        next_link = json['links'].get('next', None)
        if next_link:
            query = parse_qs(urlparse(json['links']['next']).query)
            # It comes back as a list but only ever one value
            cursor = query['page[cursor]'][0]
        else:
            cursor = 0

        return json, cursor
    else:
        logging.error("Error receiving data from datacite REST API")

    return None, None


def api_get_paging_with_url(url, params):
    """Page results from API via retrieving the next url"""

    response = api_call_get(url, params)

    if response.status_code == 200:
        json = response.json()
        if 'links' in json:
            next_link = json["links"].get("next", None)
        else:
            next_link = None
        return json, next_link
    else:
        logging.error("Error receiving data from datacite REST API")


def api_call_get(url, params=None):
    """Make authenticated get request to API with params"""

    payload_str = ''
    if params:
        # Construct the payload as a string
        # to avoid direct urlencoding by requests library which messes up some of the params
        payload_str = "&".join("%s=%s" % (k, v)
                               for k, v in params.items() if v is not None)

    response = requests.get(
        url,
        params=payload_str,
        auth=requests.auth.HTTPBasicAuth(
            config.DATACITE_API_ADMIN_USERNAME, config.DATACITE_API_ADMIN_PASSWORD),
        timeout=30
    )

    return response
