"""Handles DB queries for retrieving metadata"""

import psycopg2
import re
from datetime import datetime
import dateutil.parser
import dateutil.tz
from viringo import config
import xml.etree.cElementTree as ET

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
        self.active = active

def construct_datacite_xml(data):
    resource = ET.Element("resource")
    resource.set("xmlns", "http://datacite.org/schema/kernel-4")
    resource.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    resource.set("xsi:schemaLocation",
                 "http://datacite.org/schema/kernel-4 http://schema.datacite.org/meta/kernel-4/metadata.xsd")

    # Add resource URL as identifier
    identifier = ET.SubElement(resource, "identifier")
    if "doi.org/" in data['item_url']:
        identifier.set("identifierType", "DOI")
        identifier.text = data['item_url'].split("doi.org/")[1]
    else:
        identifier.set("identifierType", "URL")
        identifier.text = data['item_url']


    # Add creators
    creators = ET.SubElement(resource, "creators")
    for creator_entry in data['dc:contributor.author']:
        creator = ET.SubElement(creators, "creator")
        creatorName = ET.SubElement(creator, "creatorName")
        creatorName.text = creator_entry

    # Add titles
    titles = ET.SubElement(resource, "titles")
    if data['title_en'] != "":
        title = ET.SubElement(titles, "title")
        title.text = data['title_en']
        title.set("xml:lang", "en")
    if data['title_fr'] != "":
        title = ET.SubElement(titles, "title")
        title.text = data['title_fr']
        title.set("xml:lang", "fr")
        if data['title_en'] != "":
            title.set("titleType", "TranslatedTitle")

    # Add publisher
    publisher = ET.SubElement(resource, "publisher")
    publisher.text = data['repository_name']

    # Add publication year
    publicationyear = ET.SubElement(resource, "publicationYear")
    publicationyear.text = data['pub_date'][:4]

    # Add subjects
    subject_and_tags = []
    subjects = ET.SubElement(resource, "subjects")
    for subject_entry in data['frdr:category_en']:
        if subject_entry not in subject_and_tags and subject_entry != "":
            subject_and_tags.append(subject_entry)
            subject = ET.SubElement(subjects, "subject")
            subject.set("xml:lang", "en")
            subject.text = subject_entry
    for subject_entry in data['frdr:category_fr']:
        if subject_entry not in subject_and_tags and subject_entry != "":
            subject_and_tags.append(subject_entry)
            subject = ET.SubElement(subjects, "subject")
            subject.set("xml:lang", "fr")
            subject.text = subject_entry
    for subject_entry in data['frdr:keywords_en']:
        if subject_entry not in subject_and_tags and subject_entry != "":
            subject_and_tags.append(subject_entry)
            subject = ET.SubElement(subjects, "subject")
            subject.set("xml:lang", "en")
            subject.text = subject_entry
    for subject_entry in data['frdr:keywords_fr']:
        if subject_entry not in subject_and_tags and subject_entry != "":
            subject_and_tags.append(subject_entry)
            subject = ET.SubElement(subjects, "subject")
            subject.set("xml:lang", "fr")
            subject.text = subject_entry

    # If subjects is empty, remove it
    if len(subjects) == 0:
        resource.remove(subjects)

    # Add contributors (contributorType "Other")
    contributors = ET.SubElement(resource, "contributors")
    for contributor_entry in data["dc:contributor"]:
        contributor = ET.SubElement(contributors, "contributor")
        contributor.set("contributorType", "Other")
        contributorName = ET.SubElement(contributor, "contributorName")
        contributorName.text = contributor_entry

    # Add FRDR as HostingInstituton
    contributor_en = ET.SubElement(contributors, "contributor")
    contributor_en.set("contributorType", "HostingInstitution")
    contributor_en.set("xml:lang", "en")
    contributorName_en = ET.SubElement(contributor_en, "contributorName")
    contributorName_en.text = "Federated Research Data Repository"
    contributor_fr = ET.SubElement(contributors, "contributor")
    contributor_fr.set("contributorType", "HostingInstitution")
    contributor_fr.set("xml:lang", "fr")
    contributorName_fr = ET.SubElement(contributor_fr, "contributorName")
    contributorName_fr.text = "Dépôt fédéré de données de recherche"

    # Add dates
    dates = ET.SubElement(resource, "dates")
    date = ET.SubElement(dates, "date")
    date.set("dateType", "Issued")
    date.text = data['pub_date']

    # Add resourceType
    resourceType = ET.SubElement(resource, "resourceType")
    resourceType.set("resourceTypeGeneral", "Dataset")
    resourceType.text = "Dataset"

    # Add alternateIdentifiers
    alternateIdentifiers = ET.SubElement(resource, "alternateIdentifiers")
    alternateIdentifier = ET.SubElement(alternateIdentifiers, "alternateIdentifier")
    alternateIdentifier.set("alternateIdentifierType", "local")
    alternateIdentifier.text = data['local_identifier']

    # Add rightsList
    rightsList = ET.SubElement(resource, "rightsList")
    for rights_entry in data['dc:rights']:
        if rights_entry != '':
            rights = ET.SubElement(rightsList, "rights")
            rights.text = rights_entry
            if "http" in rights_entry:
                rights.set("rightsURI", rights_entry[rights_entry.find("http"):].strip())
                rights.text = rights_entry[:rights_entry.find("http")].strip()
    if len(data["frdr:access"]) > 0:
        for access_entry in data["frdr:access"]:
            rights = ET.SubElement(rightsList, "rights")
            if access_entry == "Public":
                rights.text = "info:eu-repo/semantics/openAccess"
            else:
                rights.text = "info:eu-repo/semantics/restrictedAccess"
    else: # Assume Public/openAccess
        rights = ET.SubElement(rightsList, "rights")
        rights.text = "info:eu-repo/semantics/openAccess"

    # Add description(s)
    descriptions = ET.SubElement(resource, "descriptions")
    for description_entry in data['dc:description_en']:
        if description_entry != "":
            description = ET.SubElement(descriptions, "description")
            description.set("descriptionType", "Abstract")
            description.set("xml:lang", "en")
            description.text = description_entry
    for description_entry in data['dc:description_fr']:
        if description_entry != "":
            description = ET.SubElement(descriptions, "description")
            description.set("descriptionType", "Abstract")
            description.set("xml:lang", "fr")
            description.text = description_entry

    # Add series (series)
    if data['series'] != "":
        description_series = ET.SubElement(descriptions, "description")
        description_series.set("descriptionType", "SeriesInformation")
        description_series.text = data['series']

    # If descriptions is empty, remove it
    if len(descriptions) == 0:
        resource.remove(descriptions)

    xml_string = ET.tostring(resource)
    return xml_string

def build_metadata(data):
    """Parse single FRDR result into metadata object"""
    result = Metadata()

    # Construct identifier compliant with OAI spec
    namespace = data['repo_oai_name']
    result.identifier = "oai:" + namespace + ":" + data['local_identifier']

    # Here we want to parse a ISO date but convert to UTC and then remove the TZinfo entirely
    # This is because OAI always works in UTC.
    created = dateutil.parser.parse(data['pub_date'])
    result.created_datetime = created.astimezone(dateutil.tz.UTC).replace(tzinfo=None)
    updated = dateutil.parser.parse(data['pub_date'])
    result.updated_datetime = updated.astimezone(dateutil.tz.UTC).replace(tzinfo=None)

    result.xml = construct_datacite_xml(data)
    result.metadata_version = None
    result.titles = [data['title_en'], data['title_fr']]
    result.creators = data['dc:contributor.author']
    result.subjects = []

    # De-duplicate subjects and tags
    for subject in data['frdr:category_en'] + data['frdr:category_fr'] + data['frdr:keywords_en'] + data['frdr:keywords_fr']:
        if subject not in result.subjects:
            result.subjects.append(subject)

    result.descriptions = data['dc:description_en'] + data['dc:description_fr']
    result.publisher = data['dc:publisher']
    result.publication_year = dateutil.parser.parse(data['pub_date']).year
    result.dates = [data['pub_date']]
    result.contributors = data['dc:contributor']
    result.funding_references = ''
    result.sizes = []
    result.geo_locations = data['frdr:geospatial']
    result.resource_types = ['Dataset']
    result.formats = []
    result.identifiers = [data['item_url']]
    result.language = ''
    result.relations = []
    result.rights = data['dc:rights']
    result.client = data['repo_oai_name']
    result.active = True

    return result


def rows_to_dict(cursor):
        newdict = []
        if cursor:
            for r in cursor:
                if r:
                    if isinstance(r, list):
                        newdict.append(r[0])
                    else:
                        newdict.append(r)
        return newdict


def assemble_record(record, db, user, password, server, port):

    if record["item_url"] is None:
        return None
        
    if int(record["deleted"]) == 1:
        return None

    if (len(record['title_en']) == 0 and len(record['title_fr']) == 0):
        return None

    con = psycopg2.connect("dbname='%s' user='%s' password='%s' host='%s' port='%s'" % (db, user, password, server, port))
    with con:
        lookup_cur = con.cursor(cursor_factory=None)

        lookup_cur.execute("SELECT coordinate_type, lat, lon FROM geospatial WHERE record_id=%s", [record["record_id"]])
        geodata = lookup_cur.fetchall()
        record["frdr:geospatial"] = []
        polycoordinates = []

        try:
            for coordinate in geodata:
                if coordinate[0] == "Polygon":
                    polycoordinates.append([float(coordinate[1]), float(coordinate[2])])
                else:
                    record["frdr:geospatial"].append({"frdr:geospatial_type": "Feature", "frdr:geospatial_geometry": {"frdr:geometry_type": coordinate[0], "frdr:geometry_coordinates": [float(coordinate[1]), float(coordinate[2])]}})
        except:
            pass

        if polycoordinates:
            record["frdr:geospatial"].append({"frdr:geospatial_type": "Feature", "frdr:geospatial_geometry": {"frdr:geometry_type": "Polygon", "frdr:geometry_coordinates": polycoordinates}})

    with con:
        from psycopg2.extras import DictCursor
        lookup_cur = con.cursor(cursor_factory=DictCursor)

        # attach the other values to the dict
        lookup_cur.execute("""SELECT creators.creator FROM creators JOIN records_x_creators on records_x_creators.creator_id = creators.creator_id WHERE records_x_creators.record_id=%s AND records_x_creators.is_contributor=0 order by records_x_creators_id asc""", [record["record_id"]])
        record["dc:contributor.author"] = rows_to_dict(lookup_cur)

        lookup_cur.execute("""SELECT affiliations.affiliation FROM affiliations JOIN records_x_affiliations on records_x_affiliations.affiliation_id = affiliations.affiliation_id WHERE records_x_affiliations.record_id=%s""", [record["record_id"]])
        record["datacite:creatorAffiliation"] = rows_to_dict(lookup_cur)

        lookup_cur.execute("""SELECT creators.creator FROM creators JOIN records_x_creators on records_x_creators.creator_id = creators.creator_id WHERE records_x_creators.record_id=%s AND records_x_creators.is_contributor=1 order by records_x_creators_id asc""", [record["record_id"]])
        record["dc:contributor"] = rows_to_dict(lookup_cur)

        lookup_cur.execute("""SELECT subjects.subject FROM subjects JOIN records_x_subjects on records_x_subjects.subject_id = subjects.subject_id WHERE records_x_subjects.record_id=%s and subjects.language = 'en' """, [record["record_id"]])
        record["frdr:category_en"] = rows_to_dict(lookup_cur)

        lookup_cur.execute("""SELECT subjects.subject FROM subjects JOIN records_x_subjects on records_x_subjects.subject_id = subjects.subject_id WHERE records_x_subjects.record_id=%s and subjects.language = 'fr' """, [record["record_id"]])
        record["frdr:category_fr"] = rows_to_dict(lookup_cur)

        lookup_cur.execute("""SELECT publishers.publisher FROM publishers JOIN records_x_publishers on records_x_publishers.publisher_id = publishers.publisher_id WHERE records_x_publishers.record_id=%s""", [record["record_id"]])
        record["dc:publisher"] = rows_to_dict(lookup_cur)

        lookup_cur.execute("""SELECT rights.rights FROM rights JOIN records_x_rights on records_x_rights.rights_id = rights.rights_id WHERE records_x_rights.record_id=%s""", [record["record_id"]])
        record["dc:rights"] = rows_to_dict(lookup_cur)

        lookup_cur.execute("SELECT description FROM descriptions WHERE record_id=%s and language='en' ", [record["record_id"]])
        record["dc:description_en"] = rows_to_dict(lookup_cur)

        lookup_cur.execute("SELECT description FROM descriptions WHERE record_id=%s and language='fr' ", [record["record_id"]])
        record["dc:description_fr"] = rows_to_dict(lookup_cur)

        lookup_cur.execute("""SELECT tags.tag FROM tags JOIN records_x_tags on records_x_tags.tag_id = tags.tag_id WHERE records_x_tags.record_id=%s and tags.language = 'en' """, [record["record_id"]])
        record["frdr:keywords_en"] = rows_to_dict(lookup_cur)

        lookup_cur.execute("""SELECT tags.tag FROM tags JOIN records_x_tags on records_x_tags.tag_id = tags.tag_id WHERE records_x_tags.record_id=%s and tags.language = 'fr' """, [record["record_id"]])
        record["frdr:keywords_fr"] = rows_to_dict(lookup_cur)

        lookup_cur.execute("""SELECT access.access FROM access JOIN records_x_access on records_x_access.access_id = access.access_id WHERE records_x_access.record_id=%s""", [record["record_id"]])
        record["frdr:access"] = rows_to_dict(lookup_cur)

    return record


def get_metadata_list(
        server,
        db,
        user,
        password,
        port,
        query=None,
        set=None,
        from_datetime=None,
        until_datetime=None,
        cursor=None
    ):

    records_con = psycopg2.connect("dbname='%s' user='%s' password='%s' host='%s' port='%s'" % (db, user, password, server, port))
    with records_con:
        db_cursor = records_con.cursor()
    records_sql = """SELECT recs.record_id, recs.title, recs.title_fr, recs.pub_date, recs.series, recs.source_url, recs.item_url, recs.deleted, recs.local_identifier, recs.modified_timestamp, repos.repository_url, repos.repository_name, repos.repository_thumbnail, repos.item_url_pattern, repos.last_crawl_timestamp, repos.homepage_url, repos.repo_oai_name FROM records recs, repositories repos WHERE recs.repository_id = repos.repository_id"""
    if set is not None and set != 'openaire_data':
        records_sql = records_sql + " AND (repos.repo_oai_name='" + set + "')"
    if from_datetime is not None:
        records_sql = records_sql + " AND recs.pub_date>='" + from_datetime + "'"
    if until_datetime is not None:
        records_sql = records_sql + " AND recs.pub_date<'" + until_datetime + "'"
    if cursor is not None:
        records_sql = records_sql + " OFFSET " + cursor
    db_cursor.execute(records_sql)

    record_set = db_cursor.fetchmany(config.RESULT_SET_SIZE)

    results = []
    for row in record_set:
        record = (dict(zip(['record_id', 'title_en', 'title_fr', 'pub_date', 'series', 'source_url', 'item_url', 'deleted', 'local_identifier', 'modified_timestamp', 'repository_url', 'repository_name', 'repository_thumbnail', 'item_url_pattern', 'last_crawl_timestamp', 'homepage_url', 'repo_oai_name'], row)))

        full_record = assemble_record(record, db, user, password, server, port)
        if full_record is not None:
            results.append(build_metadata(full_record))

    if cursor is not None:
        return results, db_cursor.rowcount, (len(record_set) + int(cursor))
    else:
        return results, db_cursor.rowcount, len(record_set)


def get_metadata(identifier, db, user, password, server, port):
    identifier = identifier[4:]
    namespace = identifier[:identifier.find(":")]
    local_identifier = identifier[identifier.find(":")+1:]
    records_con = psycopg2.connect("dbname='%s' user='%s' password='%s' host='%s' port='%s'" % (db, user, password, server, port))
    with records_con:
        records_cursor = records_con.cursor()
    records_sql = ("""SELECT recs.record_id, recs.title, recs.title_fr, recs.pub_date, recs.series, recs.source_url, 
    recs.item_url, recs.deleted, recs.local_identifier, recs.modified_timestamp, repos.repository_url, 
    repos.repository_name, repos.repository_thumbnail, repos.item_url_pattern, repos.last_crawl_timestamp, 
    repos.homepage_url, repos.repo_oai_name FROM records recs, repositories repos 
    WHERE recs.repository_id = repos.repository_id 
        AND recs.local_identifier =\'""" + local_identifier + "\'" + "AND repos.repo_oai_name=\'""" + namespace + "\'")
    records_cursor.execute(records_sql)
    row = records_cursor.fetchone()
    record = (dict(zip(['record_id', 'title_en', 'title_fr', 'pub_date', 'series', 'source_url', 'item_url', 'deleted', 'local_identifier', 'modified_timestamp', 'repository_url', 'repository_name', 'repository_thumbnail', 'item_url_pattern', 'last_crawl_timestamp', 'homepage_url', 'repo_oai_name'], row)))

    full_record = assemble_record(record, db, user, password, server, port)
    return build_metadata(full_record)


def get_sets(db, user, password, server, port):
    repos_con = psycopg2.connect("dbname='%s' user='%s' password='%s' host='%s' port='%s'" % (db, user, password, server, port))
    with repos_con:
        repos_cursor = repos_con.cursor()

    results = []
    results.append(['openaire_data', 'OpenAIRE'])

    repos_cursor.execute("SELECT repo_oai_name, repository_name from repositories")
    results.extend(repos_cursor.fetchall())

    return results, len(results)