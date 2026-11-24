from fdp.api import db_connection
from fdp.assets import Asset, load_assets, main_assets
from fdp.inspect import ensure_tables_exist
from fdp.selectors import expand_asset_selectors
from fdp.targets import r2

TARGETS = {"r2": r2.publish}


def publish(target: str, selectors: list[str] | None = None) -> None:
    assets = publishable_assets(selectors)

    with db_connection(read_only=True) as conn:
        ensure_tables_exist(conn, assets)
        TARGETS[target](assets, conn)


def publishable_assets(selectors: list[str] | None) -> list[Asset]:
    if not selectors:
        assets = main_assets()
        if not assets:
            raise ValueError("No main assets found.")
        return assets

    resolved_selectors = expand_asset_selectors(selectors)
    loaded = load_assets(resolved_selectors, include_dependencies=False)
    assets = [loaded.assets[key] for key in sorted(loaded.ordered_keys)]
    unsupported_assets = [asset.key for asset in assets if asset.schema != "main"]
    if unsupported_assets:
        raise ValueError(
            f"Publish only supports main assets: {', '.join(unsupported_assets)}"
        )
    return assets
