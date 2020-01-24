"""Handles DB queries for retrieving metadata"""

import psycopg2
import re
from datetime import datetime
import dateutil.parser
import dateutil.tz
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


def build_metadata(data):
    """Parse single postgres result into metadata object"""
    result = Metadata()

    result.identifier = data['record_id']

    # Here we want to parse a ISO date but convert to UTC and then remove the TZinfo entirely
    # This is because OAI always works in UTC.
    created = dateutil.parser.parse(data['pub_date'])
    result.created_datetime = created.astimezone(dateutil.tz.UTC).replace(tzinfo=None)
    updated = dateutil.parser.parse(data['pub_date'])
    result.updated_datetime = updated.astimezone(dateutil.tz.UTC).replace(tzinfo=None)

    result.xml = None

    # TODO: should I not be hardcoding this for datacite? add other fields based on current XML export
    result.metadata_version = 4

    result.titles = [data['title']]
    result.creators = data['dc:contributor.author']
    result.subjects = data['dc:subject']
    result.descriptions = data['dc:description']
    result.publisher = data['dc:publisher']
    result.publication_year = dateutil.parser.parse(data['pub_date']).year
    result.dates = [data['pub_date']]
    result.contributors = data['dc:contributor']
    result.funding_references = []
    result.sizes = []
    result.geo_locations = data['frdr:geospatial']
    result.resource_types = []
    result.formats = []
    result.identifiers = []
    result.language = ''
    result.relations = []
    result.rights = data['dc:rights']
    result.client = ''
    result.active = True

    return result


def construct_local_url(record):
        # Check if the local_identifier has already been turned into a url
        if "http" in record["local_identifier"].lower():
            return record["local_identifier"]

        # Check for OAI format of identifier (oai:domain:id)
        oai_id = None
        oai_search = re.search("oai:(.+):(.+)", record["local_identifier"])
        if oai_search:
            oai_id = oai_search.group(2)
            oai_id = oai_id.replace("_", ":")

        # If given a pattern then substitue in the item ID and return it
        if "item_url_pattern" in record and record["item_url_pattern"]:
            if oai_id:
                local_url = re.sub("(\%id\%)", oai_id, record["item_url_pattern"])
            else:
                local_url = re.sub("(\%id\%)", record["local_identifier"], record["item_url_pattern"])
            return local_url

        # Check if the identifier is a DOI
        doi = re.search("(doi|DOI):\s?\S+", record["local_identifier"])
        if doi:
            doi = doi.group(0).rstrip('\.')
            local_url = re.sub("(doi|DOI):\s?", "https://dx.doi.org/", doi)
            return local_url

        # If the item has a source URL, use it
        if ('source_url' in record) and record['source_url']:
            return record['source_url']

        # URL is in the identifier
        local_url = re.search("(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?",
                              record["local_identifier"])
        if local_url:
            return local_url.group(0)

        local_url = None
        return local_url


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


def assemble_record(record, db, user, password, server):
    record["dc:source"] = construct_local_url(record)
    if record["dc:source"] is None:
        return None
        
    if int(record["deleted"]) == 1:
        return None

    if (len(record['title']) == 0):
        return None

    con = psycopg2.connect("dbname='%s' user='%s' password='%s' host='%s'" % (db, user, password, server))
    with con:
        lookup_cur = con.cursor(cursor_factory=None)

        lookup_cur.execute("SELECT coordinate_type, lat, lon FROM geospatial WHERE record_id=?",
                        (record["record_id"],))
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
        lookup_cur = con.cursor(cursor_factory=DictCursor)

        # attach the other values to the dict
        lookup_cur.execute("""SELECT creators.creator FROM creators JOIN records_x_creators on records_x_creators.creator_id = creators.creator_id WHERE records_x_creators.record_id=? AND records_x_creators.is_contributor=0 order by records_x_creators_id asc""", (record["record_id"],))
        record["dc:contributor.author"] = rows_to_dict(lookup_cur)

        lookup_cur.execute("""SELECT affiliations.affiliation FROM affiliations JOIN records_x_affiliations on records_x_affiliations.affiliation_id = affiliations.affiliation_id WHERE records_x_affiliations.record_id=?""", (record["record_id"],))
        record["datacite:creatorAffiliation"] = rows_to_dict(lookup_cur)

        lookup_cur.execute("""SELECT creators.creator FROM creators JOIN records_x_creators on records_x_creators.creator_id = creators.creator_id WHERE records_x_creators.record_id=? AND records_x_creators.is_contributor=1 order by records_x_creators_id asc""", (record["record_id"],))
        record["dc:contributor"] = rows_to_dict(lookup_cur)

        lookup_cur.execute("""SELECT subjects.subject FROM subjects JOIN records_x_subjects on records_x_subjects.subject_id = subjects.subject_id WHERE records_x_subjects.record_id=?""", (record["record_id"],))
        record["dc:subject"] = rows_to_dict(lookup_cur)

        lookup_cur.execute("""SELECT publishers.publisher FROM publishers JOIN records_x_publishers on records_x_publishers.publisher_id = publishers.publisher_id WHERE records_x_publishers.record_id=?""", (record["record_id"],))
        record["dc:publisher"] = rows_to_dict(lookup_cur)

        lookup_cur.execute("""SELECT rights.rights FROM rights JOIN records_x_rights on records_x_rights.rights_id = rights.rights_id WHERE records_x_rights.record_id=?""", (record["record_id"],))
        record["dc:rights"] = rows_to_dict(lookup_cur)

        lookup_cur.execute("SELECT description FROM descriptions WHERE record_id=? and language='en' "), (record["record_id"],)
        record["dc:description"] = rows_to_dict(lookup_cur)

        lookup_cur.execute("SELECT description FROM descriptions WHERE record_id=? and language='fr' "), (record["record_id"],)
        record["frdr:description_fr"] = rows_to_dict(lookup_cur)

        lookup_cur.execute("""SELECT tags.tag FROM tags JOIN records_x_tags on records_x_tags.tag_id = tags.tag_id WHERE records_x_tags.record_id=? and tags.language = 'en' """, (record["record_id"],))
        record["frdr:tags"] = rows_to_dict(lookup_cur)

        lookup_cur.execute("""SELECT tags.tag FROM tags JOIN records_x_tags on records_x_tags.tag_id = tags.tag_id WHERE records_x_tags.record_id=? and tags.language = 'fr' """, (record["record_id"],))
        record["frdr:tags_fr"] = rows_to_dict(lookup_cur)

        lookup_cur.execute("""SELECT access.access FROM access JOIN records_x_access on records_x_access.access_id = access.access_id WHERE records_x_access.record_id=?""", (record["record_id"],))
        record["frdr:access"] = rows_to_dict(lookup_cur)

    return record


def get_metadata_list(
        query=None,
        provider_id=None,
        client_id=None,
        cursor=None,
        server,
        db,
        user,
        password
    ):

    # TODO: support listing by set

    # Trigger cursor navigation with a starting value
    if not cursor:
        cursor = 1
        records_con = psycopg2.connect("dbname='%s' user='%s' password='%s' host='%s'" % (db, user, password, server))
        with records_con:
            records_cursor = records_con.cursor()
        records_sql = """SELECT recs.record_id, recs.title, recs.pub_date, recs.contact, recs.series, recs.source_url, recs.deleted, recs.local_identifier, recs.modified_timestamp, repos.repository_url, repos.repository_name, repos.repository_thumbnail, repos.item_url_pattern, repos.last_crawl_timestamp FROM records recs, repositories repos WHERE recs.repository_id = repos.repository_id"""
        records_cursor.execute(records_sql)

    record_set = records_cursor.fetchmany(config.RESULT_SET_SIZE)
    results = []
    for row in record_set:
        record = (dict(zip(['record_id', 'title', 'pub_date', 'contact', 'series', 'source_url', 'deleted', 'local_identifier', 'modified_timestamp', 'repository_url', 'repository_name', 'repository_thumbnail', 'item_url_pattern', 'last_crawl_timestamp'], row)))

        full_record = assemble_record(record, db, user, password, server)
        if full_record is not None:
            results.append(build_metadata(full_record))

    cursor += config.RESULT_SET_SIZE
    # TODO: Probably need to pass rowcount back to this function for Postgres output
    return results, records_cursor.rowcount, cursor


def get_metadata(identifier, db, user, password, server):
    records_con = psycopg2.connect("dbname='%s' user='%s' password='%s' host='%s'" % (db, user, password, server))
    with records_con:
        records_cursor = records_con.cursor()
    # TODO: record_id is kind of a meaningless identifier, support local identifier + source URL
    records_sql = ("""SELECT recs.record_id, recs.title, recs.pub_date, recs.contact, recs.series, recs.source_url, recs.deleted, recs.local_identifier, recs.modified_timestamp, repos.repository_url, repos.repository_name, repos.repository_thumbnail, repos.item_url_pattern, repos.last_crawl_timestamp FROM records recs, repositories repos WHERE recs.repository_id = repos.repository_id AND recs.record_id =?""", (identifier,))
    records_cursor.execute(records_sql)
    row = records_cursor.fetchone()
    record = (dict(zip(['record_id', 'title', 'pub_date', 'contact', 'series', 'source_url', 'deleted', 'local_identifier', 'modified_timestamp', 'repository_url', 'repository_name', 'repository_thumbnail', 'item_url_pattern', 'last_crawl_timestamp'], row)))

    full_record = assemble_record(record, db, user, password, server)
    return build_metadata(full_record)


def get_sets():
    repos_con = psycopg2.connect("dbname='%s' user='%s' password='%s' host='%s'" % (db, user, password, server))
    with repos_con:
        repos_cursor = repos_con.cursor()

    repos_cursor.execute("SELECT repository_name from repositories")
    sets = repos_cursor.fetchall()
    # TODO: Format this properly to return it like the DataCite response
    return None