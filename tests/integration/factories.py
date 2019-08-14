import datetime
import factory

from viringo.services.datacite import Metadata


class MetadataFactory(factory.Factory):
    """Constructs test data for a Metadata result object"""
    class Meta:
        model = Metadata

    identifier = '10.5072/not-a-real-doi'
    created_datetime = datetime.datetime(2018, 3, 17, 6, 33)
    xml = b'<?xml version="1.0" encoding="UTF-8"?>\n<resource xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://datacite.org/schema/kernel-4" xsi:schemaLocation="http://datacite.org/schema/kernel-4 http://schema.datacite.org/meta/kernel-4/metadata.xsd">\n  <identifier identifierType="DOI">10.5072/not-a-real-doi</identifier>\n  <creators>\n    <creator>\n      <creatorName nameType="Personal">Fenner, Martin</creatorName>\n      <givenName>Martin</givenName>\n      <familyName>Fenner</familyName>\n      <nameIdentifier nameIdentifierScheme="ORCID" schemeURI="https://orcid.org">https://orcid.org/0000-0003-1419-2405</nameIdentifier>\n      <affiliation affiliationIdentifier="https://ror.org/04wxnsj81" affiliationIdentifierScheme="ROR">DataCite</affiliation>\n    </creator>\n    <creator>\n      <creatorName nameType="Personal">Hallett, Richard</creatorName>\n      <givenName>Richard</givenName>\n      <familyName>Hallett</familyName>\n      <nameIdentifier nameIdentifierScheme="ORCID" schemeURI="https://orcid.org">https://orcid.org/0000-0002-8599-0773</nameIdentifier>\n      <affiliation affiliationIdentifier="https://ror.org/04wxnsj81" affiliationIdentifierScheme="ROR">DataCite</affiliation>\n    </creator>\n  </creators>\n  <titles>\n    <title>This is a fake DOI with fake metadata.</title>\n  </titles>\n  <publisher>DataCite</publisher>\n  <publicationYear>2018</publicationYear>\n  <resourceType resourceTypeGeneral="Text">BlogPosting</resourceType>\n  <subjects>\n    <subject>datacite</subject>\n  </subjects>\n  <dates>\n    <date dateType="Issued">2018-01-18</date>\n    <date dateType="Created">2018-01-18</date>\n    <date dateType="Updated">2018-01-18</date>\n  </dates>\n  <relatedIdentifiers>\n    <relatedIdentifier relatedIdentifierType="DOI" relationType="IsPartOf" resourceTypeGeneral="Text">10.5072/related-not-a-real-doi</relatedIdentifier>\n  </relatedIdentifiers>\n  <version>1.0</version>\n  <rightsList>\n    <rights/>\n  </rightsList>\n  <descriptions>\n    <description descriptionType="Abstract">This is a fake DOI with fake metadata.</description>\n  </descriptions>\n  <geoLocations>\n    <geoLocation/>\n  </geoLocations>\n</resource>\n'
    titles = ['This is a fake DOI with fake metadata.']
    creators = ['Fenner, Martin', 'Hallett, Richard']
    subjects = ['datacite']
    descriptions = ['This is a fake DOI with fake metadata.']
    publisher = 'DataCite'
    publication_year = 2018
    dates = [
        {'type': 'Issued', 'date': '2018-01-18'},
        {'type': 'Created', 'date': '2018-01-18'},
        {'type': 'Updated', 'date': '2018-01-18'}
    ]
    contributors = []
    resource_types = ['Text', 'BlogPosting']
    funding_references = []
    geo_locations = [{}]
    formats = []
    identifiers = [
        {'type': 'DOI', 'identifier': '10.5072/not-a-real-doi'}
    ]
    language = ''
    relations = [
        {'type': 'DOI', 'identifier': '10.5072/related-not-a-real-doi'}
    ]
    rights = []
    sizes = []
    client = 'DATACITE.DATACITE'
    active = True
