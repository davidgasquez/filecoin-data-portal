import importlib
from collections.abc import Callable

import duckdb

from fdp.api import db_connection, ensure_tables_exist
from fdp.assets import Asset, main_assets

PublishTarget = Callable[[list[Asset], duckdb.DuckDBPyConnection], None]

TARGET_MODULES = {
    "gsheet": "fdp.targets.gsheet",
    "r2": "fdp.targets.r2",
}


def available_targets() -> list[str]:
    return sorted(TARGET_MODULES)


def publish(target: str) -> None:
    target_publish = load_target(target)
    assets = main_assets()
    if not assets:
        raise ValueError("No main assets found.")

    with db_connection(read_only=True) as conn:
        ensure_tables_exist(conn, assets)
        target_publish(assets, conn)


def load_target(name: str) -> PublishTarget:
    try:
        module_name = TARGET_MODULES[name]
    except KeyError as exc:
        available = ", ".join(available_targets())
        raise ValueError(
            f"Unknown publish target '{name}'. Available targets: {available}"
        ) from exc

    module = importlib.import_module(module_name)
    publish = getattr(module, "publish", None)
    if not callable(publish):
        raise TypeError(f"Publish target module is invalid: {module_name}")
    return publish
