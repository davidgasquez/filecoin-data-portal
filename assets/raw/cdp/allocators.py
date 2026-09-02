# asset.description = Allocator records from the Compliance Data Platform API.

# asset.materialization = dataframe

# asset.column = application_json_url | Allocator Registry application URL.
# asset.column = metapathway_type | Allocator metapathway type.
# asset.column = application_audit | Allocator application audit type.
# asset.column = data_type | Allocator data type.
# asset.column = address_id | Filecoin allocator actor id address.
# asset.column = address | Filecoin allocator address.
# asset.column = audit_trail | Audit trail URL.
# asset.column = retries | Upstream retry counter.
# asset.column = name | Allocator name.
# asset.column = org_name | Allocator organization name.
# asset.column = removed | Whether the allocator is inactive.
# asset.column = initial_allowance | Initial datacap allowance in bytes as text.
# asset.column = allowance | Current datacap allowance in bytes as text.
# asset.column = is_inferred | Whether the allocator is inferred upstream.
# asset.column = is_multisig | Whether the allocator address is a multisig.
# asset.column = created_at_height | Chain height when the allocator was created.
# asset.column = issue_create_timestamp | Issue creation Unix timestamp.
# asset.column = create_message_timestamp | Creation message Unix timestamp.
# asset.column = remaining_datacap | Remaining datacap in bytes as text.
# asset.column = verified_clients_count | Number of verified clients served.
# asset.column = received_datacap_change | Two-week datacap received in bytes.
# asset.column = received_datacap_change_90_days | 90-day datacap received in bytes.
# asset.column = address_eth | EVM address.
# asset.column = dc_source | Datacap source identifier.
# asset.column = is_virtual | Whether the allocator is virtual.
# asset.column = is_meta_allocator | Whether the allocator is a meta allocator.
# asset.column = received_datacap_from_meta_allocator | Datacap from a meta allocator.
# asset.column = allowance_array | Raw allowance history entries.
# asset.column = allocators_using_meta_allocator | Allocators using this meta allocator.
# asset.column = meta_allocators | Meta allocators serving this allocator.
# asset.column = audit_status | Allocator audit status.
# asset.column = latest_client_allocation_height | Latest allocation chain height.
# asset.column = fetched_at | Snapshot fetch timestamp.

# asset.not_null = address_id
# asset.unique = address_id

import datetime as dt

import httpx
import polars as pl

URL = "https://cdp.allocator.tech/allocators"
COLUMN_RENAMES = {
    "applicationJsonUrl": "application_json_url",
    "metapathwayType": "metapathway_type",
    "applicationAudit": "application_audit",
    "dataType": "data_type",
    "addressId": "address_id",
    "auditTrail": "audit_trail",
    "orgName": "org_name",
    "initialAllowance": "initial_allowance",
    "inffered": "is_inferred",
    "isMultisig": "is_multisig",
    "createdAtHeight": "created_at_height",
    "issueCreateTimestamp": "issue_create_timestamp",
    "createMessageTimestamp": "create_message_timestamp",
    "remainingDatacap": "remaining_datacap",
    "verifiedClientsCount": "verified_clients_count",
    "receivedDatacapChange": "received_datacap_change",
    "receivedDatacapChange90Days": "received_datacap_change_90_days",
    "addressEth": "address_eth",
    "dcSource": "dc_source",
    "isVirtual": "is_virtual",
    "isMetaAllocator": "is_meta_allocator",
    "receivedDatacapFromMetaallocator": "received_datacap_from_meta_allocator",
    "allowanceArray": "allowance_array",
    "allocatorsUsingMetaallocator": "allocators_using_meta_allocator",
    "metaallocators": "meta_allocators",
    "auditStatus": "audit_status",
    "latestClientAllocationHeight": "latest_client_allocation_height",
}
COLUMNS = (
    "application_json_url",
    "metapathway_type",
    "application_audit",
    "data_type",
    "address_id",
    "address",
    "audit_trail",
    "retries",
    "name",
    "org_name",
    "removed",
    "initial_allowance",
    "allowance",
    "is_inferred",
    "is_multisig",
    "created_at_height",
    "issue_create_timestamp",
    "create_message_timestamp",
    "remaining_datacap",
    "verified_clients_count",
    "received_datacap_change",
    "received_datacap_change_90_days",
    "address_eth",
    "dc_source",
    "is_virtual",
    "is_meta_allocator",
    "received_datacap_from_meta_allocator",
    "allowance_array",
    "allocators_using_meta_allocator",
    "meta_allocators",
    "audit_status",
    "latest_client_allocation_height",
)


def allocators() -> pl.DataFrame:
    data = httpx.get(URL, follow_redirects=True, timeout=60).raise_for_status().json()
    return (
        pl
        .DataFrame(data["data"], infer_schema_length=None, strict=False)
        .rename(COLUMN_RENAMES)
        .select(COLUMNS)
        .with_columns(fetched_at=pl.lit(dt.datetime.now(dt.UTC).replace(tzinfo=None)))
    )
