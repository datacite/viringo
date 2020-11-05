import datetime
import factory

from viringo.services.datacite import Metadata


class MetadataFactory(factory.Factory):
    """Constructs test data for a Metadata result object"""
    class Meta:
        model = Metadata

    identifier = '10.5072/not-a-real-doi'
    created_datetime = datetime.datetime(2018, 3, 17, 6, 33)
    updated_datetime = datetime.datetime(2018, 3, 17, 6, 33)

    xml = '''<resource xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns="http://datacite.org/schema/kernel-4"
    xsi:schemaLocation="http://datacite.org/schema/kernel-4
    http://schema.datacite.org/meta/kernel-4/metadata.xsd">
    <identifier identifierType="DOI">10.5072/not-a-real-doi</identifier>
    <creators>
        <creator>
            <creatorName nameType="Personal">Fenner, Martin</creatorName>
            <givenName>Martin</givenName>
            <familyName>Fenner</familyName>
            <nameIdentifier nameIdentifierScheme="ORCID" schemeURI="https://orcid.org">
            https://orcid.org/0000-0003-1419-2405</nameIdentifier>
            <affiliation
                affiliationIdentifier="https://ror.org/04wxnsj81"
                affiliationIdentifierScheme="ROR">DataCite
            </affiliation>
        </creator>
        <creator>
            <creatorName nameType="Personal">Hallett, Richard</creatorName>
            <givenName>Richard</givenName>
            <familyName>Hallett</familyName>
            <nameIdentifier nameIdentifierScheme="ORCID" schemeURI="https://orcid.org">
            https://orcid.org/0000-0002-8599-0773</nameIdentifier>
            <affiliation
                affiliationIdentifier="https://ror.org/04wxnsj81"
                affiliationIdentifierScheme="ROR">DataCite
            </affiliation>
        </creator>
    </creators>
    <titles>
      <title>This is a fake DOI with fake metadata.</title>
    </titles>
    <publisher>DataCite</publisher>
    <publicationYear>2018</publicationYear>
    <resourceType resourceTypeGeneral="Text">BlogPosting</resourceType>
    <subjects><subject>datacite</subject></subjects>
    <dates>
      <date dateType="Issued">2018-01-18</date>
      <date dateType="Created">2018-01-18</date>
      <date dateType="Updated">2018-01-18</date>
    </dates>
    <relatedIdentifiers>
      <relatedIdentifier relatedIdentifierType="DOI" relationType="IsPartOf"
    resourceTypeGeneral="Text">10.5072/related-not-a-real-doi</relatedIdentifier>
    </relatedIdentifiers>
    <version>1.0</version>
    <rightsList>
      <rights/>
    </rightsList>
    <descriptions>
      <description descriptionType="Abstract">This is a fake DOI with fake metadata.</description>
    </descriptions>
    <geoLocations>
      <geoLocation/>
    </geoLocations>
    </resource>
    '''
    metadata_version = 4
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
    provider = 'DATACITE'
    active = True
