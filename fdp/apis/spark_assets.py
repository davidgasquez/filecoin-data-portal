import polars as pl
import dagster as dg
from web3 import Web3
from dag_json import decode
from carbox.car import read_car
from dagster_duckdb import DuckDBResource

from fdp.resources import HttpClientResource


@dg.asset(compute_kind="python")
def raw_spark_retrievals_onchain_data(
    context: dg.AssetExecutionContext,
    duckdb: DuckDBResource,
    httpx_api: HttpClientResource,
) -> dg.MaterializeResult:
    """
    Spark retrievals onchain data.
    """

    rpc_url = "https://filecoin.chainup.net/rpc/v1"
    abi_url = "https://raw.githubusercontent.com/filecoin-station/spark-rsr-contract/refs/heads/main/out/SparkRsr.sol/SparkRsr.json"
    contract_address = "0x620bfc5AdE7eeEE90034B05DC9Bb5b540336ff90"

    response = httpx_api.get(abi_url)
    abi_json = response.json()
    abi = abi_json["abi"]

    provider = Web3(Web3.HTTPProvider(rpc_url))

    contract_address = Web3.to_checksum_address(contract_address)
    contract = provider.eth.contract(address=contract_address, abi=abi)

    results_cids = []
    i = 0

    while True:
        try:
            cid_info = {}
            cid = contract.functions.providerRetrievalResultStats(i).call()
            cid_info["cid"] = cid
            cid_info["index"] = i
            results_cids.append(cid_info)
            i += 1
        except Exception as e:
            context.log.error(f"Error fetching retrieval result stats. {e}")
            break

    context.log.info(f"Found {len(results_cids)} commitments")

    data = []

    for cid_info in results_cids:
        cid = cid_info["cid"]

        context.log.info(f"Fetching CAR for CID {cid}, index {cid_info['index']}")

        url = f"https://{cid}.ipfs.w3s.link/?format=car"

        response = httpx_api.get(url, timeout=300)

        context.log.info(f"CAR response: {response.status_code}")

        if response.status_code != 200:
            print(
                f"Error fetching retrieval result stats for CID {cid}. Status code: {response.status_code}. Response: {response.text}"
            )
            continue

        _, blocks = read_car(response.content, validate=True)
        main_block = blocks[0]

        json_data = decode(main_block.data)
        json_data["retrieval_result_stats_cid"] = str(cid)  # type: ignore
        json_data["index"] = cid_info["index"]  # type: ignore

        if "meta" in json_data:  # type: ignore
            del json_data["meta"]  # type: ignore

        data.append(json_data)

    context.log.info(f"Downloaded and parsed {len(data)} Spark retrievals stats CARs")

    flattened_data = [
        {
            **stats,
            "date": record["date"],
            "cid": record["retrieval_result_stats_cid"],
            "index": record["index"],
        }
        for record in data
        for stats in record["providerRetrievalResultStats"]
    ]

    df = pl.DataFrame(flattened_data).rename({"providerId": "provider_id"})

    asset_name = context.asset_key.to_user_string()
    with duckdb.get_connection() as con:
        con.sql(f"create or replace table raw.{asset_name} as select * from df")

    context.log.info(f"Persisted {df.height} rows to raw.{asset_name}")

    return dg.MaterializeResult(metadata={"dagster/row_count": df.height})
