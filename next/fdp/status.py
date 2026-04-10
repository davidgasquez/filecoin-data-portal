from fdp.api import (
    db_connection,
    find_assets_root,
    materialized_tables,
    quote_identifier,
)
from fdp.assets import discover_assets


def show_status() -> None:
    assets_root = find_assets_root()
    assets = discover_assets(assets_root)
    asset_keys = set(assets)

    with db_connection(read_only=True) as conn:
        tables = materialized_tables(conn)

    missing_keys = sorted(
        asset_keys - {table_key(schema, name) for schema, name in tables}
    )
    orphaned_tables = sorted(
        (schema, name)
        for schema, name in tables
        if table_key(schema, name) not in asset_keys
    )
    if not missing_keys and not orphaned_tables:
        return

    project_root = assets_root.parent
    print(f"assets: {len(assets)}")
    print(f"materialized tables: {len(tables)}")

    if missing_keys:
        print()
        print("missing in db:")
        for key in missing_keys:
            asset = assets[key]
            rel_path = asset.path.relative_to(project_root).as_posix()
            print(f"  - {asset.key} ({rel_path})")

    if orphaned_tables:
        print()
        print("orphaned in db:")
        for schema, name in orphaned_tables:
            print(f"  - {table_key(schema, name)}")

    raise SystemExit(1)


def prune_tables() -> None:
    assets_root = find_assets_root()
    assets = discover_assets(assets_root)
    asset_keys = set(assets)

    with db_connection(read_only=True) as conn:
        tables = materialized_tables(conn)

    orphaned_tables = sorted(
        (schema, name)
        for schema, name in tables
        if table_key(schema, name) not in asset_keys
    )
    if not orphaned_tables:
        print("Nothing to prune.")
        return

    with db_connection() as conn:
        for schema, name in orphaned_tables:
            conn.execute(f"drop table if exists {quoted_table_key(schema, name)}")
            print(f"dropped: {table_key(schema, name)}")


def table_key(schema: str, name: str) -> str:
    return f"{schema}.{name}"


def quoted_table_key(schema: str, name: str) -> str:
    return f"{quote_identifier(schema)}.{quote_identifier(name)}"
