import oaipmh.server


def test_decode_resumption_token_raises_no_error():
    EXAMPLE_RESUMPTION = "metadataPrefix%3Ddatacite%26set%3DSND.BOLIN%26paging_cursor%3DMTU4NTU2NDkxMTAwMCwxMC4xNzA0My9zd2VydXMtMjAxNC1kMTNj%26cursor%3D1"
    try:
        oaipmh.server.decodeResumptionToken(EXAMPLE_RESUMPTION)
    except Exception as exc:
        assert False, f"DecodingResumptionToken raised an exception {exc}"


