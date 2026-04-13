# asset.description = Flattened DatacapStats verified client allowance history
# records from raw.datacapstats_verified_clients.allowance_array.
# asset.depends = raw.datacapstats_verified_clients

# asset.column = verified_client_row_id | DatacapStats verified client row id
# from the parent snapshot row.
# asset.column = verified_client_address | Filecoin verified client address.
# asset.column = verified_client_name | Verified client display name.
# asset.column = verifier_name | Allocator display name from the parent client
# snapshot.
# asset.column = allowance_id | DatacapStats allowance history row id.
# asset.column = error | Upstream allowance processing error, if any.
# asset.column = height | Chain height when this allowance entry was created.
# asset.column = message_ref | Upstream message identifier from msgCID;
# usually a CID but not always.
# asset.column = retries | Upstream retry counter for the allowance entry.
# asset.column = dc_source | Datacap source identifier.
# asset.column = address_id | Filecoin actor id address for the verified client.
# asset.column = allowance | Allowance granted in bytes as text.
# asset.column = audit_trail | Audit trail URL for this allowance entry.
# asset.column = allowance_ttd | Time-to-data value attributed upstream, if any.
# asset.column = is_data_public | Upstream public-data classification.
# asset.column = issue_creator | Issue creator identifier attributed upstream.
# asset.column = provider_list | Provider ids associated with the allowance
# entry.
# asset.column = used_allowance | Used allowance in bytes as text.
# asset.column = is_ldn_allowance | Whether the allowance is tagged as LDN.
# asset.column = is_efil_allowance | Whether the allowance is tagged as eFIL.
# asset.column = verifier_address_id | Filecoin actor id address of the
# allocator that issued datacap.
# asset.column = is_from_autoverifier | Whether the allowance came from the
# autoverifier flow.
# asset.column = retrieval_frequency | Retrieval frequency attributed upstream.
# asset.column = searched_by_proposal | Whether the allocation was searched by
# proposal upstream.
# asset.column = issue_create_timestamp | Issue creation Unix timestamp.
# asset.column = has_remaining_allowance | Whether the allowance still has
# remaining datacap upstream.
# asset.column = create_message_timestamp | Creation message Unix timestamp.
# asset.column = fetched_at | Snapshot fetch timestamp inherited from the
# parent verified client snapshot.

import polars as pl

from fdp.api import table

COLUMN_RENAMES = {
    "id": "allowance_id",
    "msgCID": "message_ref",
    "dcSource": "dc_source",
    "addressId": "address_id",
    "auditTrail": "audit_trail",
    "allowanceTTD": "allowance_ttd",
    "isDataPublic": "is_data_public",
    "issueCreator": "issue_creator",
    "providerList": "provider_list",
    "usedAllowance": "used_allowance",
    "isLdnAllowance": "is_ldn_allowance",
    "isEFilAllowance": "is_efil_allowance",
    "verifierAddressId": "verifier_address_id",
    "isFromAutoverifier": "is_from_autoverifier",
    "retrievalFrequency": "retrieval_frequency",
    "searchedByProposal": "searched_by_proposal",
    "issueCreateTimestamp": "issue_create_timestamp",
    "hasRemainingAllowance": "has_remaining_allowance",
    "createMessageTimestamp": "create_message_timestamp",
}
STRING_COLUMNS_WITH_EMPTY_AS_NULL = (
    "error",
    "is_data_public",
    "issue_creator",
    "retrieval_frequency",
)


def verified_client_allowances() -> pl.DataFrame:
    clients = table("raw.datacapstats_verified_clients")
    allowances = (
        clients
        .select(
            pl.col("id").alias("verified_client_row_id"),
            pl.col("address").alias("verified_client_address"),
            pl.col("name").alias("verified_client_name"),
            "verifier_name",
            "fetched_at",
            "allowance_array",
        )
        .explode("allowance_array")
        .filter(pl.col("allowance_array").is_not_null())
        .unnest("allowance_array")
        .rename(COLUMN_RENAMES)
        .with_columns([
            pl
            .when(pl.col(column) == "")
            .then(None)
            .otherwise(pl.col(column))
            .alias(column)
            for column in STRING_COLUMNS_WITH_EMPTY_AS_NULL
        ])
    )
    return allowances
