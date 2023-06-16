import urllib
import zstandard
import ijson
import json

STATE_MARKET_DEALS_URL = (
    "https://marketdeals.s3.amazonaws.com/StateMarketDeals.json.zst"
)


def get_state_market_deals():
    # Download the file
    # curl -o /tmp/StateMarketDeals.json.zst https://marketdeals.s3.amazonaws.com/StateMarketDeals.json.zst
    urllib.request.urlretrieve(
        STATE_MARKET_DEALS_URL,
        "/tmp/StateMarketDeals.json.zst",
    )

    # Decompress the file
    # zstd -d /tmp/StateMarketDeals.json.zst -o /tmp/StateMarketDeals.json
    dctx = zstandard.ZstdDecompressor()
    with open("/tmp/StateMarketDeals.json.zst", "rb") as fh:
        stream_reader = dctx.stream_reader(fh)
        output = stream_reader.read()
        with open("/tmp/StateMarketDeals.json", "wb") as f:
            f.write(output)

    # Parse the file
    # jq --stream 'fromstream(1|truncate_stream(inputs))' \
    #   -c /tmp/StateMarketDeals.json \
    #   > /tmp/ParsedStateMarketDeals.json
    with open("/tmp/ParsedStateMarketDeals.json", "w") as f:
        for k, v in ijson.kvitems(open("/tmp/StateMarketDeals.json"), ""):
            v["DealID"] = k
            f.write(json.dumps(v) + "\n")
