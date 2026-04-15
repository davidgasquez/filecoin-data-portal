from pathlib import Path

from fdp.assets import load_assets
from fdp.inspect import AssetView, inspect_assets
from fdp.selectors import expand_asset_selectors
from fdp.tabular import render_text_table


def show_asset(selector: str, sample_rows: int = 5) -> None:
    if sample_rows < 1:
        raise ValueError("sample_rows must be at least 1")

    resolved_selectors = expand_asset_selectors([selector])
    if not resolved_selectors:
        raise ValueError(f"Unknown selector: {selector}")
    if len(resolved_selectors) != 1:
        count = len(resolved_selectors)
        raise ValueError(
            f"show expects exactly one asset, got {count} from '{selector}'"
        )

    asset_key = resolved_selectors[0]
    loaded = load_assets([asset_key], include_dependencies=False)
    asset_view = inspect_assets(
        loaded,
        asset_keys=[asset_key],
        include_row_count=True,
        sample_rows=sample_rows,
    )[0]
    print_asset_view(asset_view, loaded.project_root)


def print_asset_view(asset_view: AssetView, project_root: Path) -> None:
    asset = asset_view.asset
    print(f"asset: {asset.key}")
    print()
    print("metadata:")
    print(f"  path: {asset.path.relative_to(project_root).as_posix()}")
    print(f"  kind: {asset.kind}")
    print(f"  description: {asset.description or 'none'}")
    print("  depends:")
    if asset.depends:
        for dependency in asset.depends:
            print(f"    - {dependency}")
    else:
        print("    - none")
    print("  columns:")
    if asset.columns:
        for column in asset.columns:
            print(f"    - {column.name}: {column.description}")
    else:
        print("    - none")
    print("  tests:")
    test_lines = asset_test_lines(asset_view, project_root)
    if test_lines:
        for line in test_lines:
            print(f"    - {line}")
    else:
        print("    - none")
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
        list(asset_view.sample_columns),
        list(asset_view.sample_rows),
        lowercase_bools=True,
    ):
        print(f"  {line}")


def asset_test_lines(asset_view: AssetView, project_root: Path) -> list[str]:
    asset = asset_view.asset
    lines = [
        *(f"not_null: {column}" for column in asset.tests.not_null),
        *(f"unique: {column}" for column in asset.tests.unique),
        *(f"assert: {assertion}" for assertion in asset.tests.assertions),
        *(
            f"custom: {custom_test.path.relative_to(project_root).as_posix()}"
            for custom_test in asset_view.custom_tests
        ),
    ]
    return lines
