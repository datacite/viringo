"""
OAI-PMH compatible catalogs for parsing data and building appropriate responses.
They conform to the oaipmh.common.ResumptionOAIPMH interface provided by the
pyoai library.
"""

from datetime import datetime
from oaipmh import common, error

from .services import datacite

class DataCiteOAIServer():
    """Build OAI-PMH data responses for DataCite metadata catalog"""
    def identify(self):
        """Construct common identification for the OAI service"""

        identify = common.Identify(
            repositoryName='DataCite',
            baseURL='https://oai.datacite.org/oai',
            protocolVersion="2.0",
            adminEmails=['support@datacite.org'],
            earliestDatestamp=datetime(2011, 1, 1),
            deletedRecord='persistent',
            granularity='YYYY-MM-DDThh:mm:ssZ',
            compression=['gzip', 'deflate'],
            toolkit_description=False)

        # Specify a custom description
        datacite_desc = """
        <oai-identifier xmlns="http://www.openarchives.org/OAI/2.0/oai-identifier" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai-identifier http://www.openarchives.org/OAI/2.0/oai-identifier.xsd">
            <scheme>oai</scheme>
            <repositoryIdentifier>oai.datacite.org</repositoryIdentifier>
            <delimiter>:</delimiter>
            <sampleIdentifier>oai:oai.datacite.org:12425</sampleIdentifier>
        </oai-identifier>
        """

        identify.add_description(xml_string=datacite_desc)

        return identify

    def getRecord(self, metadataPrefix, identifier):
        #pylint: disable=no-self-use,invalid-name
        """Returns pyoai data tuple for specific record"""

        # We just want the DOI out of the OAI identifier.
        _, doi = identifier.split(':')

        result = datacite.get_metadata(doi)
        if not result:
            raise error.IdDoesNotExistError(
                "\"%s\" is unknown or illegal in this repository" % identifier
            )

        # Build metadata based on requested format and result
        metadata = {}
        if metadataPrefix == "oai_dc":
            metadata = self.build_dc_metadata_map(result)

        data = self.build_record(result, metadata)

        return data

    def listRecords(
            self,
            metadataPrefix=None,
            from_=None,
            until=None,
            set_=None,
            paging_cursor=None
        ):
        #pylint: disable=no-self-use,invalid-name
        """Returns pyoai data tuple for list of records"""

        # Get both a provider and client_id from the set
        client_id = None
        provider_id = None

        # DataCite API deals in lowercase
        if set_:
            set_.lower()
            if "." in set_:
                provider_id, client_id = set_.split(".")
            else:
                provider_id = set_.lower()

        results, paging_cursor = datacite.get_metadata_list(
            provider_id=provider_id,
            client_id=client_id,
            from_datetime=from_,
            until_datetime=until,
            cursor=paging_cursor
        )

        records = []
        if results:
            for result in results:
                # Build metadata based on requested format and result
                metadata = {}
                if metadataPrefix == "oai_dc":
                    metadata = self.build_dc_metadata_map(result)

                data = self.build_record(result, metadata)

                records.append(data)

        # This differs from the pyoai implementation in that we have to return a cursor here
        # But this is okay as we have a custom server to handle it.
        return records, paging_cursor

    def build_record(self, result, metadata):
        """Construct a OAI-PMH data payload for a record"""

        # Provider symbol can just be extracted from the client symbol
        provider_symbol, _ = result.client.split(".")

        data = (
            common.Header(
                None,
                'doi:' + result.identifier,
                result.created_datetime,
                setspec=[provider_symbol, result.client],
                deleted=not result.active
            ),
            common.Metadata(
                None,
                metadata
            ),
            None # About string - not used
        )

        return data

    def build_dc_metadata_map(self, result):
        """Construct a metadata map object for DC writing"""
        dates = []
        if result.publication_year:
            dates.append(str(result.publication_year))
        dates.extend([date['type'] + ": " + str(date['date']) for date in result.dates])

        rights = []
        for right in result.rights:
            if right['statement']:
                rights.append(right['statement'])
            if right['uri']:
                rights.append(right['uri'])

        identifiers = [
            identifier_to_string(identifier) for identifier in result.identifiers
        ]

        relations = [
            identifier_to_string(relation)
            for relation in result.relations
        ]

        contributors = [
            contributor.get('name') for contributor in result.contributors
        ]

        metadata = {
            'title': result.titles,
            'creator': result.creators,
            'subject': result.subjects,
            'description': result.descriptions,
            'publisher': [result.publisher] if result.publisher else [],
            'contributor': contributors,
            'date': dates,
            'type': result.resource_types,
            'format': result.formats,
            'identifier': identifiers,
            'relation': relations,
            'language': [result.language] if result.language else [],
            'rights': rights,
        }

        return metadata


def identifier_to_string(identifier):
    """Take an identifier and return in a formatted in single string"""
    _id = identifier.get('identifier')
    _type = identifier.get('type') or ''
    return _type.lower() + ":" + _id
