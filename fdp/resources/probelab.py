"""ProbeLab Filecoin Onchain Cloud daily Parquet backups of Dealbot checks."""

import base64
import csv
import datetime as dt
import hashlib
import io
import tempfile
import time

import httpx

import fdp
from fdp.api import quote_identifier, table_exists

INDEX_URL = "https://probelab.io/filecoin/foc/backups/export.csv"
START_DATE = dt.date(2026, 5, 26)
GATEWAYS = ("https://ipfs.filebase.io/ipfs/", "https://gateway.pinata.cloud/ipfs/")
PROVIDER_PIECE_URLS = {"1": "https://main.ezpdpz.net/piece/"}
RAW_SHA256_CID_PREFIX = bytes([1, 0x55, 0x12, 0x20])


def raw_cid_bytes(cid: str) -> bytes:
    decoded = base64.b32decode(cid[1:].upper() + "=" * (-len(cid[1:]) % 8))
    if not cid.startswith("b") or decoded[:4] != RAW_SHA256_CID_PREFIX:
        raise ValueError(f"Unsupported backup CID {cid}")
    return decoded


def matches_cid(cid: str, data: bytes) -> bool:
    return hashlib.sha256(data).digest() == raw_cid_bytes(cid)[4:]


def car_section_length(car: bytes, offset: int) -> tuple[int, int]:
    length = 0
    for index, byte in enumerate(car[offset : offset + 9]):
        length |= (byte & 0x7F) << (7 * index)
        if byte < 0x80:
            return length, offset + index + 1
    raise ValueError("Invalid CAR section length")


def car_root_block(car: bytes, cid: str) -> bytes | None:
    root = raw_cid_bytes(cid)
    try:
        # A CARv1 has a length-prefixed header followed by length-prefixed blocks.
        header_length, offset = car_section_length(car, 0)
        offset += header_length
        while offset < len(car):
            length, start = car_section_length(car, offset)
            offset = start + length
            if length == 0 or offset > len(car):
                break
            if car.startswith(root, start, offset):
                return car[start + len(root) : offset]
    except ValueError:
        return None
    return None


def fetch_verified(
    client: httpx.Client, cid: str, piece_url: str | None = None
) -> bytes:
    urls = [gateway + cid for gateway in GATEWAYS]
    if piece_url:
        urls.append(piece_url)
    for attempt in range(5):
        for url in urls:
            try:
                response = client.get(url)
            except httpx.HTTPError:
                continue
            if response.status_code != 200:
                continue
            if matches_cid(cid, response.content):
                return response.content
            if url == piece_url:
                block = car_root_block(response.content, cid)
                if block is not None and matches_cid(cid, block):
                    return block
        time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"Backup {cid} unavailable from {', '.join(urls)}")


def replace_backup(conn, table: str, day: str, cid: str, path: str) -> None:
    conn.execute(
        "create or replace temp table backup as "
        f"select *, ?::date as backup_date, ?::text as backup_cid "
        f"from read_parquet('{path}')",
        [day, cid],
    )
    conn.execute(f"create table if not exists {table} as from backup limit 0")
    existing = {row[0] for row in conn.execute(f"describe {table}").fetchall()}
    for name, column_type, *_ in conn.execute("describe backup").fetchall():
        if name not in existing:
            column = quote_identifier(name)
            conn.execute(f"alter table {table} add column {column} {column_type}")
    conn.execute("begin")
    conn.execute(f"delete from {table} where backup_date = ?", [day])
    conn.execute(f"insert into {table} by name from backup")
    conn.execute("commit")
    conn.execute("drop table backup")


def load_backups(dataset: str, table: str) -> None:
    """Load new or changed daily backups for one check type into a raw table."""
    yesterday = dt.datetime.now(dt.UTC).date() - dt.timedelta(days=1)
    schema, name = table.split(".")
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        index = client.get(
            INDEX_URL,
            params={"dataset": dataset, "from": str(START_DATE), "to": str(yesterday)},
        ).raise_for_status()
        backups = sorted(
            (
                row
                for row in csv.DictReader(io.StringIO(index.text))
                if row["date"] <= yesterday.isoformat()
            ),
            key=lambda row: (row["date"], row["root_cid"]),
        )
        with fdp.db_connection() as conn:
            conn.execute(f"create schema if not exists {schema}")
            loaded = set()
            if table_exists(conn, schema, name):
                loaded = set(
                    conn.execute(
                        f"select distinct backup_date::text, backup_cid from {table}"
                    ).fetchall()
                )
            for row in backups:
                day, cid = row["date"], row["root_cid"]
                if (day, cid) in loaded:
                    continue
                provider = PROVIDER_PIECE_URLS.get(row.get("provider_id") or "")
                piece_cid = row.get("piece_cid") or ""
                piece_url = (
                    provider + piece_cid if provider and piece_cid.isalnum() else None
                )
                # Empty backups add no rows, so they are fetched again next run.
                with tempfile.NamedTemporaryFile(suffix=".parquet") as file:
                    file.write(fetch_verified(client, cid, piece_url))
                    file.flush()
                    replace_backup(conn, table, day, cid, file.name)
