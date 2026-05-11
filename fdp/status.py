from fdp.api import (
    db_connection,
    default_db_path,
    materialized_tables,
    quote_table_key,
)
from fdp.assets import load_assets


def show_status() -> None:
    loaded = load_assets()
    assets = loaded.assets
    asset_keys = set(assets)

    with db_connection(read_only=True) as conn:
        tables = materialized_tables(conn)

    missing_keys = sorted(asset_keys - {f"{schema}.{name}" for schema, name in tables})
    orphaned_tables = sorted(
        (schema, name)
        for schema, name in tables
        if f"{schema}.{name}" not in asset_keys
    )
    if not missing_keys and not orphaned_tables:
        return

    print(f"assets: {len(assets)}")
    print(f"materialized tables: {len(tables)}")

    if missing_keys:
        print()
        print("missing in db:")
        for key in missing_keys:
            asset = assets[key]
            rel_path = asset.path.relative_to(loaded.project_root).as_posix()
            print(f"  - {asset.key} ({rel_path})")

    if orphaned_tables:
        print()
        print("orphaned in db:")
        for schema, name in orphaned_tables:
            print(f"  - {schema}.{name}")

    raise SystemExit(1)


def prune_tables() -> None:
    db_path = default_db_path()
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        print("Nothing to prune.")
        return

    assets = load_assets().assets
    asset_keys = set(assets)

    with db_connection(read_only=True) as conn:
        tables = materialized_tables(conn)

    orphaned_tables = sorted(
        (schema, name)
        for schema, name in tables
        if f"{schema}.{name}" not in asset_keys
    )
    if not orphaned_tables:
        print("Nothing to prune.")
        return

    with db_connection() as conn:
        for schema, name in orphaned_tables:
            conn.execute(f"drop table if exists {quote_table_key(schema, name)}")
            print(f"dropped: {schema}.{name}")
