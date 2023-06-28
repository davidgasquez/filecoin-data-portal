import urllib
import zstandard
import ijson
import json


def model(dbt, session):
    dbt.config(materialized="external")

    urllib.request.urlretrieve(
        "https://marketdeals.s3.amazonaws.com/StateMarketDeals.json.zst",
        "/tmp/StateMarketDeals.json.zst",
    )

    dctx = zstandard.ZstdDecompressor()
    input_path = "/tmp/StateMarketDeals.json.zst"
    output_path = "/tmp/ParsedStateMarketDeals.json"

    with open(input_path, "rb") as ifh, open(output_path, "wb") as ofh:
        reader = dctx.stream_reader(ifh)
        for k, v in ijson.kvitems(reader, ""):
            v["DealID"] = k
            ofh.write(json.dumps(v).encode("utf-8") + b"\n")

    query = """
    select
        DealID,
        Proposal.*,
        State.*
    from read_ndjson_auto("/tmp/ParsedStateMarketDeals.json")
    """

    return session.query(query)
