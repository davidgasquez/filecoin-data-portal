# asset.description = Raw verified client records from the getVerifiedClients API.

# asset.materialization = dataframe

# asset.column = id | DatacapStats verified client row id.
# asset.column = address_id | Filecoin actor id address.
# asset.column = address | Filecoin verified client address.
# asset.column = retries | Upstream retry counter.
# asset.column = audit_trail | Audit trail URL.
# asset.column = name | Verified client display name.
# asset.column = org_name | Verified client organization name.
# asset.column = initial_allowance | Initial datacap allowance in bytes as text.
# asset.column = allowance | Current datacap allowance in bytes as text.
# asset.column = verifier_address_id | Filecoin actor id address of the allocator.
# asset.column = created_at_height | Chain height when the verified client was created.
# asset.column = issue_create_timestamp | Issue creation Unix timestamp.
# asset.column = create_message_timestamp | Creation message Unix timestamp.
# asset.column = verifier_name | Allocator display name.
# asset.column = deal_count | Number of verified deals attributed upstream.
# asset.column = provider_count | Number of storage providers attributed upstream.
# asset.column = top_provider | Top storage provider attributed upstream.
# asset.column = received_datacap_change | Received datacap change in bytes.
# asset.column = used_datacap_change | Used datacap change in bytes.
# asset.column = allowance_array | Raw allowance history entries.
# asset.column = region | Region attributed upstream.
# asset.column = website | Website attributed upstream.
# asset.column = industry | Industry attributed upstream.
# asset.column = received_datacap_change_90_days | 90-day datacap received change.
# asset.column = used_datacap_change_90_days | 90-day datacap used change in bytes.
# asset.column = used_datacap | Used datacap in bytes as text.
# asset.column = remaining_datacap | Remaining datacap in bytes as text.
# asset.column = fetched_at | Snapshot fetch timestamp.

import datetime as dt

import httpx
import polars as pl

URL = "https://api.datacapstats.io/api/getVerifiedClients"
COLUMN_RENAMES = {
    "addressId": "address_id",
    "auditTrail": "audit_trail",
    "orgName": "org_name",
    "initialAllowance": "initial_allowance",
    "verifierAddressId": "verifier_address_id",
    "createdAtHeight": "created_at_height",
    "issueCreateTimestamp": "issue_create_timestamp",
    "createMessageTimestamp": "create_message_timestamp",
    "verifierName": "verifier_name",
    "dealCount": "deal_count",
    "providerCount": "provider_count",
    "topProvider": "top_provider",
    "receivedDatacapChange": "received_datacap_change",
    "usedDatacapChange": "used_datacap_change",
    "allowanceArray": "allowance_array",
    "receivedDatacapChange90Days": "received_datacap_change_90_days",
    "usedDatacapChange90Days": "used_datacap_change_90_days",
    "usedDatacap": "used_datacap",
    "remainingDatacap": "remaining_datacap",
}


def verified_clients() -> pl.DataFrame:
    data = httpx.get(URL, follow_redirects=True, timeout=30).raise_for_status().json()
    return (
        pl
        .DataFrame(data["data"], infer_schema_length=None, strict=False)
        .rename(COLUMN_RENAMES)
        .with_columns(fetched_at=pl.lit(dt.datetime.now(dt.UTC).replace(tzinfo=None)))
    )
