# asset.description = Client records from the Compliance Data Platform API.

# asset.materialization = dataframe

# asset.column = id | Filecoin client actor id address.
# asset.column = address | Filecoin client address.
# asset.column = name | Client name.
# asset.column = application_url | Client application URL.
# asset.column = datacap_received | Datacap received in bytes as text.
# asset.column = datacap_remaining | Datacap remaining in bytes as text.
# asset.column = datacap_used_2_weeks | Two-week datacap use in bytes as text.
# asset.column = datacap_used_90_days | 90-day datacap use in bytes as text.
# asset.column = fetched_at | Snapshot fetch timestamp.

# asset.not_null = id
# asset.unique = id

import datetime as dt

import httpx
import polars as pl

URL = "https://cdp.allocator.tech/clients"
COLUMN_RENAMES = {
    "githubUrl": "application_url",
    "datacapReceived": "datacap_received",
    "datacapRemaining": "datacap_remaining",
    "datacapUsed2Weeks": "datacap_used_2_weeks",
    "datacapUsed90Days": "datacap_used_90_days",
}
COLUMNS = (
    "id",
    "address",
    "name",
    "application_url",
    "datacap_received",
    "datacap_remaining",
    "datacap_used_2_weeks",
    "datacap_used_90_days",
)


def clients() -> pl.DataFrame:
    data = httpx.get(URL, follow_redirects=True, timeout=30).raise_for_status().json()
    return (
        pl
        .DataFrame(data["data"], infer_schema_length=None, strict=False)
        .rename(COLUMN_RENAMES)
        .select(COLUMNS)
        .with_columns(fetched_at=pl.lit(dt.datetime.now(dt.UTC).replace(tzinfo=None)))
    )
