from pathlib import Path

from fdp.assets import CustomSqlTest, load_assets
from fdp.inspect import AssetView, inspect_asset
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

    asset_key = resolved_selectors[0]
    asset_view = inspect_asset(loaded.assets[asset_key], sample_rows)
    print_asset_view(
        asset_view, loaded.custom_tests_by_asset[asset_key], loaded.project_root
    )


def print_items(label: str, items: list[str]) -> None:
    print(f"  {label}:")
    for item in items or ["none"]:
        print(f"    - {item}")


def print_asset_view(
    asset_view: AssetView,
    custom_tests: tuple[CustomSqlTest, ...],
    project_root: Path,
) -> None:
    asset = asset_view.asset
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
                for t in custom_tests
            ),
        ],
    )
    print()
    print("materialized:")
    print(f"  exists: {'yes' if asset_view.exists else 'no'}")
    if not asset_view.exists:
        return
    print(f"  rows: {asset_view.row_count}")
    print("  columns:")
    for column in asset_view.columns:
        print(f"    - {column.name}: {column.data_type}")
    print()
    print("sample:")
    for line in render_text_table(
        asset_view.sample_columns,
        asset_view.sample_rows,
        lowercase_bools=True,
    ):
        print(f"  {line}")
