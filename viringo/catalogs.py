"""
OAI-PMH compatible catalogs for parsing data and building appropriate responses.
They conform to the oaipmh.common.ResumptionOAIPMH interface provided by the
pyoai library.
"""

import base64
import binascii
import logging
from datetime import datetime
from oaipmh import common, error

from viringo import config
from .services import datacite
from .services import frdr

class DataCiteOAIServer():
    """Build OAI-PMH data responses for DataCite metadata catalog"""
    def identify(self):
        """Construct common identification for the OAI service"""

        identify = common.Identify(
            repositoryName=config.OAIPMH_REPOS_NAME,
            baseURL=config.OAIPMH_BASE_URL,
            protocolVersion="2.0",
            adminEmails=[config.OAIPMH_ADMIN_EMAIL],
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

    def listMetadataFormats(self, identifier=None):
        #pylint: disable=no-self-use,invalid-name
        """Returns metadata formats available for the repository

        Identifier does nothing as our repository responds in all formats for all dois
        """
        # PyOAI Expects result format (metadataPrefix, schema, metadataNamespace)

        format_oai_dc = (
            'oai_dc',
            'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
            'http://www.openarchives.org/OAI/2.0/oai_dc/'
        )

        format_oai_datacite = (
            'oai_datacite',
            'http://schema.datacite.org/oai/oai-1.1/oai.xsd',
            'http://schema.datacite.org/oai/oai-1.1/'
        )

        format_datacite = (
            'datacite',
            'http://schema.datacite.org/meta/nonexistant/nonexistant.xsd',
            'http://datacite.org/schema/nonexistant'
        )

        return [format_oai_dc, format_oai_datacite, format_datacite]

    def getRecord(self, metadataPrefix, identifier):
        #pylint: disable=no-self-use,invalid-name
        """Returns pyoai data tuple for specific record"""

        # We just want the DOI out of the OAI identifier.
        _, doi = identifier.split(':', 1)

        result = datacite.get_metadata(doi)
        if not result:
            raise error.IdDoesNotExistError(
                "\"%s\" is unknown or illegal in this repository" % identifier
            )

        # Build metadata based on requested format and result
        metadata = self.build_metadata_map(result)

        header = self.build_header(result)
        record = self.build_record(metadata)
        data = (
            header,
            record,
            None # About string - not used
        )

        return data

    def listRecords(
            self,
            metadataPrefix=None,
            from_=None,
            until=None,
            set=None,
            paging_cursor=None
        ):
        #pylint: disable=no-self-use,invalid-name
        """Returns pyoai data tuple for list of records"""

        # If available get the search query from the set param
        search_query = set_to_search_query(set)

        # Get both a provider and client_id from the set
        provider_id, client_id = set_to_provider_client(set)
        results, total_records, paging_cursor = datacite.get_metadata_list(
            query=search_query,
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
                metadata = self.build_metadata_map(result)

                header = self.build_header(result)
                record = self.build_record(metadata)

                data = (
                    header,
                    record,
                    None # About string - not used
                )

                records.append(data)

        # This differs from the pyoai implementation in that we have to return a cursor here
        # But this is okay as we have a custom server to handle it.
        return records, total_records, paging_cursor

    def listIdentifiers(
            self,
            metadataPrefix=None,
            from_=None,
            until=None,
            set=None,
            paging_cursor=None
        ):
        #pylint: disable=no-self-use,invalid-name
        """Returns pyoai data tuple for list of identifiers"""

        # Get both a provider and client_id from the set
        provider_id, client_id = set_to_provider_client(set)

        results, total_records, paging_cursor = datacite.get_metadata_list(
            provider_id=provider_id,
            client_id=client_id,
            from_datetime=from_,
            until_datetime=until,
            cursor=paging_cursor
        )

        records = []
        if results:
            for result in results:
                header = self.build_header(result)

                records.append(header)

        # This differs from the pyoai implementation in that we have to return a cursor here
        # But this is okay as we have a custom server to handle it.
        return records, total_records, paging_cursor

    def listSets(
            self,
            paging_cursor=0
        ):
        #pylint: disable=no-self-use,invalid-name
        """Returns pyoai data tuple for list of sets"""

        # Note this implementation is not super efficient as we request
        # the full set everytime regardles of actual paging
        # The paging is handled just by offsetting the records returned.
        # This is however acceptable given sets are a small subset of data.

        # We know we're always dealing with a integer value here
        paging_cursor = int(paging_cursor)

        batch_size = 50
        next_batch = paging_cursor + batch_size
        results, total_results = datacite.get_sets()
        results = results[paging_cursor: next_batch]

        if len(results) < batch_size:
            paging_cursor = None
        else:
            paging_cursor = next_batch

        records = []
        if results:
            for identifier, name in results:
                # Format of a set is setSpec, setName, setDescription
                records.append((identifier.upper(), name, None))

        # This differs from the pyoai implementation in that we have to return a cursor here
        # But this is okay as we have a custom server to handle it.
        return records, total_results, paging_cursor

    def build_header(self, result):
        """Construct a OAI-PMH record header"""

        # Provider symbol can just be extracted from the client symbol
        provider_symbol, _ = result.client.split(".")

        return common.Header(
            None,
            'doi:' + result.identifier,
            result.updated_datetime,
            setspec=[provider_symbol, result.client],
            deleted=not result.active
        )

    def build_record(self, metadata):
        """Construct a OAI-PMH payload for a record"""

        return common.Metadata(
            None,
            metadata
        )

    def build_metadata_map(self, result):
        """Construct a metadata map object for oai metadata writing"""
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
            'xml': result.xml,
            'set': result.client,
            'metadata_version': result.metadata_version
        }

        return metadata


class FRDROAIServer():
    """Build OAI-PMH responses from the FRDR Postgres server"""
    def identify(self):
        """Construct common identification for the OAI service"""

        identify = common.Identify(
            repositoryName=config.OAIPMH_REPOS_NAME,
            baseURL=config.OAIPMH_BASE_URL,
            protocolVersion="2.0",
            adminEmails=[config.OAIPMH_ADMIN_EMAIL],
            earliestDatestamp=datetime(2011, 1, 1),
            deletedRecord='persistent',
            granularity='YYYY-MM-DDThh:mm:ssZ',
            compression=['gzip', 'deflate'],
            toolkit_description=False)

        # Specify a custom description
        frdr_desc = """
        <oai-identifier xmlns="http://www.openarchives.org/OAI/2.0/oai-identifier" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai-identifier http://www.openarchives.org/OAI/2.0/oai-identifier.xsd">
            <scheme>oai</scheme>
            <repositoryIdentifier>""" + config.OAIPMH_IDENTIFIER + """</repositoryIdentifier>
            <delimiter>:</delimiter>
            <sampleIdentifier>oai""" + config.OAIPMH_IDENTIFIER + """:1</sampleIdentifier>
        </oai-identifier>
        """

        identify.add_description(xml_string=frdr_desc)

        return identify

    def listMetadataFormats(self, identifier=None):
        #pylint: disable=no-self-use,invalid-name
        """Returns metadata formats available for the repository

        Identifier does nothing as our repository responds in all formats for all dois
        """
        # PyOAI Expects result format (metadataPrefix, schema, metadataNamespace)

        format_oai_dc = (
            'oai_dc',
            'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
            'http://www.openarchives.org/OAI/2.0/oai_dc/'
        )

        format_oai_datacite = (
            'oai_datacite',
            'http://schema.datacite.org/oai/oai-1.1/oai.xsd',
            'http://schema.datacite.org/oai/oai-1.1/'
        )

        format_datacite = (
            'datacite',
            'http://schema.datacite.org/meta/nonexistant/nonexistant.xsd',
            'http://datacite.org/schema/nonexistant'
        )

        return [format_oai_dc, format_oai_datacite, format_datacite]

    def getRecord(self, metadataPrefix, identifier):
        #pylint: disable=no-self-use,invalid-name
        """Returns pyoai data tuple for specific record"""

        # Should we implement this based on source_url and local_identifier the way we currently do for the harvester? 

        result = frdr.get_metadata(identifier, db, user, password, server)
        if not result:
            raise error.IdDoesNotExistError(
                "\"%s\" is unknown or illegal in this repository" % identifier
            )

        # Build metadata based on requested format and result
        metadata = self.build_metadata_map(result)

        header = self.build_header(result)
        record = self.build_record(metadata)
        data = (
            header,
            record,
            None # About string - not used
        )

        return data

    def listRecords(
            self,
            metadataPrefix=None,
            from_=None,
            until=None,
            set=None,
            paging_cursor=None
        ):
        #pylint: disable=no-self-use,invalid-name
        """Returns pyoai data tuple for list of records"""

        # If available get the search query from the set param
        search_query = set_to_search_query(set)

        # From and until parameters aren't supported with FRDR
        # Get both a provider and client_id from the set
        provider_id, client_id = set_to_provider_client(set)
        results, total_records, paging_cursor = frdr.get_metadata_list(
            query=search_query,
            provider_id=provider_id,
            client_id=client_id,
            cursor=paging_cursor,
            server=config.POSTGRES_SERVER,
            db=config.POSTGRES_DB,
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD
        )

        records = []
        if results:
            for result in results:
                # Build metadata based on requested format and result
                metadata = self.build_metadata_map(result)

                header = self.build_header(result)
                record = self.build_record(metadata)

                data = (
                    header,
                    record,
                    None # About string - not used
                )

                records.append(data)

        # This differs from the pyoai implementation in that we have to return a cursor here
        # But this is okay as we have a custom server to handle it.
        return records, total_records, paging_cursor

    def listIdentifiers(
            self,
            metadataPrefix=None,
            from_=None,
            until=None,
            set=None,
            paging_cursor=None
        ):
        #pylint: disable=no-self-use,invalid-name
        """Returns pyoai data tuple for list of identifiers"""

        # Get both a provider and client_id from the set
        provider_id, client_id = set_to_provider_client(set)

        results, total_records, paging_cursor = frdr.get_metadata_list(
            query=search_query,
            provider_id=provider_id,
            client_id=client_id,
            cursor=paging_cursor,
            server=config.POSTGRES_SERVER,
            db=config.POSTGRES_DB,
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD
        )

        records = []
        if results:
            for result in results:
                header = self.build_header(result)

                records.append(header)

        # This differs from the pyoai implementation in that we have to return a cursor here
        # But this is okay as we have a custom server to handle it.
        return records, total_records, paging_cursor

    def listSets(
            self,
            paging_cursor=0
        ):
        #pylint: disable=no-self-use,invalid-name
        """Returns pyoai data tuple for list of sets"""

        # Note this implementation is not super efficient as we request
        # the full set everytime regardles of actual paging
        # The paging is handled just by offsetting the records returned.
        # This is however acceptable given sets are a small subset of data.

        # We know we're always dealing with a integer value here
        paging_cursor = int(paging_cursor)

        batch_size = 50
        next_batch = paging_cursor + batch_size
        results, total_results = frdr.get_sets()
        results = results[paging_cursor: next_batch]

        if len(results) < batch_size:
            paging_cursor = None
        else:
            paging_cursor = next_batch

        records = []
        if results:
            for identifier, name in results:
                # Format of a set is setSpec, setName, setDescription
                records.append((identifier.upper(), name, None))

        # This differs from the pyoai implementation in that we have to return a cursor here
        # But this is okay as we have a custom server to handle it.
        return records, total_results, paging_cursor

    def build_header(self, result):
        """Construct a OAI-PMH record header"""

        # Provider symbol can just be extracted from the client symbol
        provider_symbol, _ = result.client.split(".")

        return common.Header(
            None,
            'doi:' + result.identifier,
            result.updated_datetime,
            setspec=[provider_symbol, result.client],
            deleted=not result.active
        )

    def build_record(self, metadata):
        """Construct a OAI-PMH payload for a record"""

        return common.Metadata(
            None,
            metadata
        )

    def build_metadata_map(self, result):
        """Construct a metadata map object for oai metadata writing"""
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
            'xml': result.xml,
            'set': result.client,
            'metadata_version': result.metadata_version
        }

        return metadata


def set_to_search_query(unparsed_set):
    """Take a oai set and extract any base64url encoded search query"""

    if unparsed_set and "~" in unparsed_set:
        _, search_query_base64 = unparsed_set.split("~")
        try:
            return base64.urlsafe_b64decode(search_query_base64).decode("utf-8")
        except binascii.Error:
            logging.debug("Unable to parse set search query")
            return ""

    return ""

def set_to_provider_client(unparsed_set):
    """Take a oai set and convert into provider_id and client_id"""

    # Get both a provider and client_id from the set
    client_id = None
    provider_id = None

    if unparsed_set:
        # Strip any additional query
        if "~" in unparsed_set:
            unparsed_set, _ = unparsed_set.split("~")

    if unparsed_set:
        # DataCite API deals in lowercase
        unparsed_set = unparsed_set.lower()
        if "." in unparsed_set:
            provider_id, _ = unparsed_set.split(".")
            client_id = unparsed_set
        else:
            provider_id = unparsed_set

    return provider_id, client_id

def identifier_to_string(identifier):
    """Take an identifier and return in a formatted in single string"""
    _id = identifier.get('identifier')
    _type = identifier.get('type') or ''
    return _type.lower() + ":" + _id
