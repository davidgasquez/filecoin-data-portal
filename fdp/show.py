from fdp.api import db_connection, table_exists
from fdp.assets import load_assets
from fdp.inspect import validate_materialized_asset
from fdp.selectors import expand_asset_selectors
from fdp.tabular import render_text_table


def show_asset(selector: str, sample_rows: int = 5) -> None:
    if sample_rows < 1:
        raise ValueError("sample_rows must be at least 1")

    loaded = load_assets()
    resolved_selectors = expand_asset_selectors(loaded, [selector])
    if len(resolved_selectors) != 1:
        count = len(resolved_selectors)
        raise ValueError(
            f"show expects exactly one asset, got {count} from '{selector}'"
        )

    asset = loaded.assets[resolved_selectors[0]]
    project_root = loaded.project_root
    with db_connection(read_only=True) as conn:
        exists = table_exists(conn, asset.schema, asset.name)
        if exists:
            columns = validate_materialized_asset(conn, asset)
            rows = conn.execute(
                f"select * from {asset.key} limit {sample_rows}"
            ).fetchall()
            total = conn.execute(f"select count(*) from {asset.key}").fetchall()[0][0]

    print(f"asset: {asset.key}")
    print()
    print("metadata:")
    print(f"  path: {asset.path.relative_to(project_root).as_posix()}")
    print(f"  kind: {asset.kind}")
    print(f"  description: {asset.description or 'none'}")
    print_items("depends", list(asset.depends))
    print_items("columns", [f"{c.name}: {c.description}" for c in asset.columns])
    print_items(
        "tests",
        [
            *(f"not_null: {column}" for column in asset.tests.not_null),
            *(f"unique: {column}" for column in asset.tests.unique),
            *(f"assert: {assertion}" for assertion in asset.tests.assertions),
            *(
                f"custom: {t.path.relative_to(project_root).as_posix()}"
                for t in loaded.custom_tests_by_asset[asset.key]
            ),
        ],
    )
    print()
    print("materialized:")
    print(f"  exists: {'yes' if exists else 'no'}")
    if not exists:
        return
    print(f"  rows: {total}")
    print("  columns:")
    for name, data_type in columns:
        print(f"    - {name}: {data_type}")
    print()
    print("sample:")
    for line in render_text_table(
        [name for name, _ in columns], rows, lowercase_bools=True
    ):
        print(f"  {line}")


def print_items(label: str, items: list[str]) -> None:
    print(f"  {label}:")
    for item in items or ["none"]:
        print(f"    - {item}")
