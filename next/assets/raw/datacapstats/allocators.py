# asset.description = Raw allocator records from the DatacapStats getVerifiers API.
# asset.materialization = dataframe

# asset.column = id | DatacapStats allocator row id.
# asset.column = address_id | Filecoin actor id address.
# asset.column = address | Filecoin allocator address.
# asset.column = name | Allocator display name.
# asset.column = org_name | Allocator organization name.
# asset.column = audit_trail | Audit trail URL.
# asset.column = retries | Upstream retry counter.
# asset.column = removed | Whether the allocator is removed upstream.
# asset.column = initial_allowance | Initial datacap allowance in bytes as text.
# asset.column = allowance | Current datacap allowance in bytes as text.
# asset.column = remaining_datacap | Remaining datacap in bytes as text.
# asset.column = received_datacap_change | Received datacap change in bytes.
# asset.column = received_datacap_change_90_days | 90-day datacap change in bytes.
# asset.column = verified_clients_count | Number of verified clients served.
# asset.column = is_inferred | Upstream inferred flag.
# asset.column = is_multisig | Whether the allocator address is a multisig.
# asset.column = is_virtual | Whether the allocator is virtual upstream.
# asset.column = is_meta_allocator | Whether the allocator is a meta allocator.
# asset.column = created_at_height | Chain height when the allocator was created.
# asset.column = issue_create_timestamp | Issue creation Unix timestamp.
# asset.column = create_message_timestamp | Creation message Unix timestamp.
# asset.column = audit_status | Upstream audit status.
# asset.column = dc_source | Datacap source identifier.
# asset.column = address_eth | EVM address if available.
# asset.column = allowance_array | Raw allowance history entries.
# asset.column = fetched_at | Snapshot fetch timestamp.

import datetime as dt

import httpx
import polars as pl

URL = "https://api.datacapstats.io/api/getVerifiers"
COLUMN_RENAMES = {
    "addressId": "address_id",
    "orgName": "org_name",
    "auditTrail": "audit_trail",
    "initialAllowance": "initial_allowance",
    "remainingDatacap": "remaining_datacap",
    "receivedDatacapChange": "received_datacap_change",
    "receivedDatacapChange90Days": "received_datacap_change_90_days",
    "verifiedClientsCount": "verified_clients_count",
    "inffered": "is_inferred",
    "isMultisig": "is_multisig",
    "isVirtual": "is_virtual",
    "isMetaAllocator": "is_meta_allocator",
    "createdAtHeight": "created_at_height",
    "issueCreateTimestamp": "issue_create_timestamp",
    "createMessageTimestamp": "create_message_timestamp",
    "auditStatus": "audit_status",
    "dcSource": "dc_source",
    "addressEth": "address_eth",
    "allowanceArray": "allowance_array",
}


def allocators() -> pl.DataFrame:
    data = httpx.get(URL, follow_redirects=True, timeout=30).raise_for_status().json()
    return (
        pl
        .DataFrame(data["data"], infer_schema_length=None, strict=False)
        .rename(COLUMN_RENAMES)
        .with_columns(fetched_at=pl.lit(dt.datetime.now(dt.UTC).replace(tzinfo=None)))
    )
