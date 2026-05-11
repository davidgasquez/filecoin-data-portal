from collections.abc import Callable

import duckdb

from fdp.api import db_connection, ensure_tables_exist
from fdp.assets import Asset, load_assets, main_assets
from fdp.selectors import expand_asset_selectors
from fdp.targets import gsheet, r2

PublishTarget = Callable[[list[Asset], duckdb.DuckDBPyConnection], None]

PUBLISH_TARGETS: dict[str, PublishTarget] = {
    "gsheet": gsheet.publish,
    "r2": r2.publish,
}


def available_targets() -> list[str]:
    return sorted(PUBLISH_TARGETS)


def publish(target: str, selectors: list[str] | None = None) -> None:
    try:
        publish_target = PUBLISH_TARGETS[target]
    except KeyError as exc:
        available = ", ".join(available_targets())
        raise ValueError(
            f"Unknown publish target '{target}'. Available targets: {available}"
        ) from exc

    assets = publishable_assets(selectors)

    with db_connection(read_only=True) as conn:
        ensure_tables_exist(conn, assets)
        publish_target(assets, conn)


def publishable_assets(selectors: list[str] | None) -> list[Asset]:
    if not selectors:
        assets = main_assets()
        if not assets:
            raise ValueError("No main assets found.")
        return assets

    resolved_selectors = expand_asset_selectors(selectors)
    loaded = load_assets(resolved_selectors, include_dependencies=False)
    selected_assets = [loaded.assets[key] for key in loaded.ordered_keys]
    unsupported_assets = sorted(
        asset.key for asset in selected_assets if asset.schema != "main"
    )
    if unsupported_assets:
        raise ValueError(
            f"Publish only supports main assets: {', '.join(unsupported_assets)}"
        )

    assets = sorted(selected_assets, key=lambda asset: asset.key)
    if not assets:
        raise ValueError("No main assets found.")
    return assets
