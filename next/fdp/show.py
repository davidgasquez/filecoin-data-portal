from fdp.api import db_connection, find_assets_root, table_exists
from fdp.assets import discover_assets
from fdp.test import asset_test_lines, render_text_table


def show_asset(name: str, sample_rows: int = 5) -> None:
    if sample_rows < 1:
        raise ValueError("sample_rows must be at least 1")

    assets_root = find_assets_root()
    assets = discover_assets(assets_root)
    try:
        asset = assets[name]
    except KeyError as exc:
        raise ValueError(f"Unknown asset: {name}") from exc

    project_root = assets_root.parent
    print(f"asset: {asset.key}")
    print(f"path: {asset.path.relative_to(project_root).as_posix()}")
    print(f"kind: {asset.kind}")
    print(f"resource: {asset.resource}")
    print(f"resolved key: {asset.key}")
    print()
    print("depends:")
    if asset.depends:
        for dependency in asset.depends:
            print(f"  - {dependency}")
    else:
        print("  - none")
    print()
    print("tests:")
    test_lines = asset_test_lines(asset, assets_root, project_root)
    if test_lines:
        for line in test_lines:
            print(f"  - {line}")
    else:
        print("  - none")
    print()
    print("sample:")
    with db_connection(read_only=True) as conn:
        if not table_exists(conn, asset.schema, asset.name):
            print("  not materialized")
            return
        cursor = conn.execute(f"select * from {asset.key} limit {sample_rows}")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
    for line in render_text_table(columns, rows, lowercase_bools=True):
        print(f"  {line}")
