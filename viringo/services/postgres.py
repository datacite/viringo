"""Handles DB queries for retrieving metadata"""

import psycopg2
import re

def construct_local_url(record):
        # Check if the local_identifier has already been turned into a url
        if "http" in record["local_identifier"].lower():
            return record["local_identifier"]

        # Check for OAI format of identifier (oai:domain:id)
        oai_id = None
        oai_search = re.search("oai:(.+):(.+)", record["local_identifier"])
        if oai_search:
            oai_id = oai_search.group(2)
            # TODO: determine if this is needed for all repos, or just SFU?
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

    records_con = psycopg2.connect("dbname='%s' user='%s' password='%s' host='%s'" % (
                    db, user, password, server))
    with records_con:
        records_cursor = records_con.cursor()

    records_sql = """SELECT recs.record_id, recs.title, recs.pub_date, recs.contact, recs.series, recs.source_url, recs.deleted, recs.local_identifier, recs.modified_timestamp,
        repos.repository_url, repos.repository_name, repos.repository_thumbnail, repos.item_url_pattern, repos.last_crawl_timestamp
        FROM records recs, repositories repos WHERE recs.repository_id = repos.repository_id"""

    records_cursor.execute(records_sql)

    # Need to see if we can somehow page the OAI response to the DB query so it only requests a fixed number at a time
    for row in records_cursor:
        record = (dict(zip(
            ['record_id', 'title', 'pub_date', 'contact', 'series', 'source_url', 'deleted', 'local_identifier',
             'modified_timestamp',
             'repository_url', 'repository_name', 'repository_thumbnail', 'item_url_pattern',
             'last_crawl_timestamp'], row)))
        record["deleted"] = int(record["deleted"])

        record["dc:source"] = construct_local_url(record)
        if record["dc:source"] is None:
            continue
            
        if record["deleted"] == 1:
            continue

        if (len(record['title']) == 0):
            continue

        con = psycopg2.connect("dbname='%s' user='%s' password='%s' host='%s'" % (
                    db, user, password, server))
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
                        record["frdr:geospatial"].append({"frdr:geospatial_type": "Feature",
                                                          "frdr:geospatial_geometry": {
                                                              "frdr:geometry_type": coordinate[0],
                                                              "frdr:geometry_coordinates": [float(coordinate[1]),
                                                                                            float(coordinate[2])]}})
            except:
                pass

            if polycoordinates:
                record["frdr:geospatial"].append({"frdr:geospatial_type": "Feature",
                                                  "frdr:geospatial_geometry": {"frdr:geometry_type": "Polygon",
                                                                               "frdr:geometry_coordinates": polycoordinates}})

        with con:
            lookup_cur = con.cursor(cursor_factory=DictCursor)

            # attach the other values to the dict
            lookup_cur.execute("""SELECT creators.creator FROM creators JOIN records_x_creators on records_x_creators.creator_id = creators.creator_id
                WHERE records_x_creators.record_id=? AND records_x_creators.is_contributor=0 order by records_x_creators_id asc""",
                            (record["record_id"],))
            record["dc:contributor.author"] = rows_to_dict(lookup_cur)

            lookup_cur.execute("""SELECT affiliations.affiliation FROM affiliations JOIN records_x_affiliations on records_x_affiliations.affiliation_id = affiliations.affiliation_id
                WHERE records_x_affiliations.record_id=?""", (record["record_id"],))
            record["datacite:creatorAffiliation"] = rows_to_dict(lookup_cur)

            lookup_cur.execute("""SELECT creators.creator FROM creators JOIN records_x_creators on records_x_creators.creator_id = creators.creator_id
                WHERE records_x_creators.record_id=? AND records_x_creators.is_contributor=1 order by records_x_creators_id asc""",
                            (record["record_id"],))
            record["dc:contributor"] = rows_to_dict(lookup_cur)

            lookup_cur.execute("""SELECT subjects.subject FROM subjects JOIN records_x_subjects on records_x_subjects.subject_id = subjects.subject_id
                WHERE records_x_subjects.record_id=?""", (record["record_id"],))
            record["dc:subject"] = rows_to_dict(lookup_cur)

            lookup_cur.execute("""SELECT publishers.publisher FROM publishers JOIN records_x_publishers on records_x_publishers.publisher_id = publishers.publisher_id
                WHERE records_x_publishers.record_id=?""", (record["record_id"],))
            record["dc:publisher"] = rows_to_dict(lookup_cur)

            lookup_cur.execute("""SELECT rights.rights FROM rights JOIN records_x_rights on records_x_rights.rights_id = rights.rights_id
                                                   WHERE records_x_rights.record_id=?""", (record["record_id"],))
            record["dc:rights"] = rows_to_dict(lookup_cur)

            lookup_cur.execute(
                "SELECT description FROM descriptions WHERE record_id=? and language='en' "),
                (record["record_id"],)
            record["dc:description"] = rows_to_dict(lookup_cur)

            lookup_cur.execute(
                "SELECT description FROM descriptions WHERE record_id=? and language='fr' "),
                (record["record_id"],)
            record["frdr:description_fr"] = rows_to_dict(lookup_cur)

            lookup_cur.execute("""SELECT tags.tag FROM tags JOIN records_x_tags on records_x_tags.tag_id = tags.tag_id
                WHERE records_x_tags.record_id=? and tags.language = 'en' """, (record["record_id"],))
            record["frdr:tags"] = rows_to_dict(lookup_cur)

            lookup_cur.execute("""SELECT tags.tag FROM tags JOIN records_x_tags on records_x_tags.tag_id = tags.tag_id
                WHERE records_x_tags.record_id=? and tags.language = 'fr' """, (record["record_id"],))
            record["frdr:tags_fr"] = rows_to_dict(lookup_cur)

            lookup_cur.execute("""SELECT access.access FROM access JOIN records_x_access on records_x_access.access_id = access.access_id
                WHERE records_x_access.record_id=?""", (record["record_id"],))
            record["frdr:access"] = rows_to_dict(lookup_cur)