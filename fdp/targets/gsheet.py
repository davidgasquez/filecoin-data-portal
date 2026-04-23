import os
from datetime import date, datetime, time
from typing import Any

import duckdb
import gspread
from gspread.utils import rowcol_to_a1

from fdp.assets import Asset, main_assets
from fdp.google import credentials_from_env

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID_ENV_VAR = "FDP_GSHEET_SPREADSHEET_ID"
MAX_EXPORT_ROWS = 100_000
UPDATE_CHUNK_ROWS = 10_000


def publish(assets: list[Asset], conn: duckdb.DuckDBPyConnection) -> None:
    spreadsheet_id = spreadsheet_id_from_env()
    client, service_account_email = gsheet_client()
    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
    except PermissionError as exc:
        raise ValueError(
            "Google Sheets access denied. Share the spreadsheet with "
            f"{service_account_email}."
        ) from exc

    total = len(assets)
    count_width = len(str(total))
    asset_width = max((len(asset.key) for asset in assets), default=0)

    for index, asset in enumerate(assets, start=1):
        row_count = publish_asset(conn, spreadsheet, asset)
        print(
            f"[{index:>{count_width}}/{total:>{count_width}}] "
            f"{asset.key:<{asset_width}} OK "
            f"rows={row_count} worksheet={asset.name}",
            flush=True,
        )

    prune_stale_worksheets(
        spreadsheet,
        valid_titles={asset.name for asset in main_assets()},
    )


def spreadsheet_id_from_env() -> str:
    spreadsheet_id = os.environ.get(SPREADSHEET_ID_ENV_VAR, "")
    if not spreadsheet_id:
        raise ValueError(f"Missing {SPREADSHEET_ID_ENV_VAR} in environment")
    return spreadsheet_id


def gsheet_client() -> tuple[gspread.Client, str]:
    credentials = credentials_from_env(scopes=SCOPES)
    return gspread.authorize(credentials), credentials.service_account_email


def publish_asset(
    conn: duckdb.DuckDBPyConnection,
    spreadsheet: gspread.Spreadsheet,
    asset: Asset,
) -> int:
    columns, rows = asset_rows(conn, asset)
    sheet_rows = max(len(rows) + 1, 1)
    sheet_cols = max(len(columns), 1)
    worksheet = ensure_worksheet(
        spreadsheet,
        asset.name,
        rows=sheet_rows,
        cols=sheet_cols,
    )
    worksheet.clear()
    worksheet.resize(rows=sheet_rows, cols=sheet_cols)
    update_worksheet(worksheet, columns, rows)
    return len(rows)


def ensure_worksheet(
    spreadsheet: gspread.Spreadsheet,
    title: str,
    *,
    rows: int,
    cols: int,
) -> gspread.Worksheet:
    try:
        return spreadsheet.worksheet(title)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=title, rows=rows, cols=cols)


def prune_stale_worksheets(
    spreadsheet: gspread.Spreadsheet,
    *,
    valid_titles: set[str],
) -> None:
    for worksheet in spreadsheet.worksheets():
        if worksheet.title in valid_titles:
            continue
        spreadsheet.del_worksheet(worksheet)
        print(f"DELETED worksheet={worksheet.title}", flush=True)


def asset_rows(
    conn: duckdb.DuckDBPyConnection,
    asset: Asset,
) -> tuple[list[str], list[list[Any]]]:
    cursor = conn.execute(f"select * from {asset.key} limit 0")
    columns = [description[0] for description in cursor.description]
    if not columns:
        raise ValueError(f"Asset has no columns: {asset.key}")

    # Main assets are materialized in the intended presentation order, so a
    # simple LIMIT keeps the most relevant rows when a worksheet must be capped.
    cursor = conn.execute(f"select * from {asset.key} limit {MAX_EXPORT_ROWS}")
    rows = [[serialize_cell(value) for value in row] for row in cursor.fetchall()]
    return columns, rows


def update_worksheet(
    worksheet: gspread.Worksheet,
    columns: list[str],
    rows: list[list[Any]],
) -> None:
    worksheet.update(values=[columns], range_name="A1", raw=True)
    for offset in range(0, len(rows), UPDATE_CHUNK_ROWS):
        chunk = rows[offset : offset + UPDATE_CHUNK_ROWS]
        start_row = offset + 2
        end_row = start_row + len(chunk) - 1
        range_name = f"A{start_row}:{rowcol_to_a1(end_row, len(columns))}"
        worksheet.update(values=chunk, range_name=range_name, raw=True)


def serialize_cell(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, (date, datetime, time)):
        return value.isoformat()
    if isinstance(value, bool | int | float | str):
        return value
    return str(value)
