import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from graphlib import CycleError, TopologicalSorter
from pathlib import Path
from typing import Literal, assert_never

from fdp.api import find_project_root

AssetKind = Literal["python", "sql"]
AssetRuntime = Literal["sql", "lily", "dataframe", "custom"]
ValidationReporter = Callable[[str, str], None]

ASSET_KIND_BY_SUFFIX: dict[str, AssetKind] = {".py": "python", ".sql": "sql"}
COMMENT_PREFIXES: dict[AssetKind, str] = {"python": "#", "sql": "--"}
SUPPORTED_METADATA_KEYS = {
    "description",
    "depends",
    "not_null",
    "unique",
    "assert",
    "column",
    "materialization",
    "resource",
    "keep_existing_on_failure",
}
SQL_RUNTIME_BY_RESOURCE: dict[str, AssetRuntime] = {"bigquery.lily": "lily"}
PYTHON_RUNTIME_BY_MATERIALIZATION: dict[str, AssetRuntime] = {
    "dataframe": "dataframe",
    "custom": "custom",
}
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
METADATA_LINE_RE = re.compile(
    r"asset\.(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)"
)


@dataclass(frozen=True)
class AssetColumn:
    name: str
    description: str


@dataclass(frozen=True)
class AssetTests:
    not_null: tuple[str, ...]
    unique: tuple[str, ...]
    assertions: tuple[str, ...]


@dataclass(frozen=True)
class CustomSqlTest:
    name: str
    path: Path


@dataclass(frozen=True)
class Asset:
    name: str
    schema: str
    key: str
    path: Path
    runtime: AssetRuntime
    keep_existing_on_failure: bool
    depends: tuple[str, ...]
    description: str | None
    columns: tuple[AssetColumn, ...]
    tests: AssetTests

    @property
    def kind(self) -> AssetKind:
        match self.runtime:
            case "sql" | "lily":
                return "sql"
            case "dataframe" | "custom":
                return "python"
            case _:
                assert_never(self.runtime)


@dataclass(frozen=True)
class LoadedAssets:
    project_root: Path
    assets: dict[str, Asset]
    ordered_keys: tuple[str, ...]
    custom_tests_by_asset: dict[str, tuple[CustomSqlTest, ...]]

    @property
    def assets_root(self) -> Path:
        return self.project_root / "assets"


def load_assets(
    *,
    reporter: ValidationReporter = lambda label, status: None,
) -> LoadedAssets:
    project_root = find_project_root()
    assets_root = project_root / "assets"
    asset_list = run_validation_step(
        "parse asset files and metadata",
        reporter,
        lambda: [
            asset_from_path(path, assets_root) for path in asset_files(assets_root)
        ],
    )
    assets = run_validation_step(
        "validate unique asset keys", reporter, lambda: index_assets(asset_list)
    )
    run_validation_step(
        "validate metadata model", reporter, lambda: validate_metadata_model(asset_list)
    )
    graph = run_validation_step(
        "validate dependencies", reporter, lambda: dependency_graph(assets)
    )
    custom_tests_by_asset = run_validation_step(
        "parse custom sql tests",
        reporter,
        lambda: collect_custom_sql_tests(assets_root, assets),
    )
    ordered_keys = tuple(
        run_validation_step(
            "validate dependency ordering",
            reporter,
            lambda: topological_order({key: graph[key] for key in sorted(assets)}),
        )
    )
    return LoadedAssets(
        project_root=project_root,
        assets=assets,
        ordered_keys=ordered_keys,
        custom_tests_by_asset=custom_tests_by_asset,
    )


def check_assets() -> None:
    load_assets(reporter=print_check_status)


def discover_assets() -> dict[str, Asset]:
    return load_assets().assets


def main_assets() -> list[Asset]:
    return sorted(
        (asset for asset in discover_assets().values() if asset.schema == "main"),
        key=lambda asset: asset.key,
    )


def asset_files(assets_root: Path) -> list[Path]:
    return sorted(
        path
        for path in assets_root.rglob("*")
        if path.is_file()
        and path.suffix in ASSET_KIND_BY_SUFFIX
        and not path.name.startswith("_")
        and not path.name.endswith(".test.sql")
    )


def validate_metadata_model(assets: Iterable[Asset]) -> None:
    for asset in assets:
        if asset.schema == "main" and not asset.columns:
            raise ValueError(
                f"Main asset {asset.key} must define asset.column metadata "
                f"in {asset.path}"
            )


def collect_custom_sql_tests(
    assets_root: Path,
    assets: dict[str, Asset],
) -> dict[str, tuple[CustomSqlTest, ...]]:
    tests_by_asset = {asset_key: [] for asset_key in assets}
    for path in sorted(assets_root.rglob("*.test.sql")):
        asset_key, test_name = custom_sql_test_identity(path, assets_root)
        if asset_key not in assets:
            raise ValueError(f"Unknown asset '{asset_key}' referenced in {path}")
        tests_by_asset[asset_key].append(CustomSqlTest(name=test_name, path=path))
    return {asset_key: tuple(tests) for asset_key, tests in tests_by_asset.items()}


def custom_sql_test_identity(path: Path, assets_root: Path) -> tuple[str, str]:
    relative_path = path.relative_to(assets_root)
    if len(relative_path.parts) < 2:
        raise ValueError(
            f"Data test path must include a schema folder under assets: {path}"
        )

    asset_name, separator, test_name = path.name.removesuffix(".test.sql").partition(
        "__"
    )
    if not separator or not test_name:
        raise ValueError(
            f"Invalid data test file name '{path}'. Expected asset__name.test.sql"
        )

    validate_identifier(test_name, "test", path)
    schema, name = asset_identity_from_path(
        path.with_name(f"{asset_name}.sql"), assets_root
    )
    return f"{schema}.{name}", test_name


def asset_from_path(path: Path, assets_root: Path) -> Asset:
    kind = ASSET_KIND_BY_SUFFIX[path.suffix]
    metadata_lines, body_lines = extract_metadata_lines(
        path.read_text(encoding="utf-8"), COMMENT_PREFIXES[kind]
    )
    metadata = parse_metadata_lines(metadata_lines, path)
    if not body_lines:
        raise ValueError(f"Asset file has no content beyond metadata: {path}")
    schema, name = asset_identity_from_path(path, assets_root)
    runtime = parse_asset_runtime(kind, metadata, path)
    keep_existing_on_failure = parse_bool_metadata(
        metadata,
        "keep_existing_on_failure",
        path,
    )

    return Asset(
        name=name,
        schema=schema,
        key=f"{schema}.{name}",
        path=path,
        runtime=runtime,
        keep_existing_on_failure=keep_existing_on_failure,
        depends=parse_dependencies(metadata.get("depends", []), path),
        description=metadata_value(metadata, "description", path),
        columns=parse_columns(metadata.get("column", []), path),
        tests=AssetTests(
            not_null=parse_column_names(metadata.get("not_null", []), path, "not_null"),
            unique=parse_column_names(metadata.get("unique", []), path, "unique"),
            assertions=parse_assertions(metadata.get("assert", []), path),
        ),
    )


def extract_metadata_lines(source: str, prefix: str) -> tuple[list[str], list[str]]:
    metadata_lines: list[str] = []
    source_lines = source.splitlines()
    body_start = len(source_lines)

    for index, line in enumerate(source_lines):
        stripped = line.lstrip()
        if not stripped:
            continue
        if stripped.startswith("#!") and not metadata_lines:
            continue
        if stripped.startswith(prefix):
            content = stripped.removeprefix(prefix).lstrip()
            if content:
                metadata_lines.append(content)
            continue
        body_start = index
        break

    return metadata_lines, source_lines[body_start:]


def parse_metadata_lines(lines: list[str], path: Path) -> dict[str, list[str]]:
    metadata: dict[str, list[str]] = {}
    current_key: str | None = None

    for line in lines:
        if line.startswith("asset."):
            match = METADATA_LINE_RE.fullmatch(line)
            if match is None:
                raise ValueError(f"Invalid asset metadata line in {path}: {line}")
            key = match.group("key")
            if key not in SUPPORTED_METADATA_KEYS:
                raise ValueError(unsupported_metadata_message(key, path))
            metadata.setdefault(key, []).append(match.group("value").strip())
            current_key = key
            continue

        if current_key is None:
            continue

        metadata[current_key][-1] = f"{metadata[current_key][-1]} {line}".strip()

    return metadata


def unsupported_metadata_message(key: str, path: Path) -> str:
    if key == "schema":
        return (
            f"Unsupported asset.schema in {path}. "
            "Schema comes from the first folder under assets."
        )
    if key == "name":
        return (
            f"Unsupported asset.name in {path}. Table names come from the asset path."
        )
    return f"Unsupported asset.{key} in {path}"


def metadata_value(
    metadata: dict[str, list[str]],
    key: str,
    path: Path,
) -> str | None:
    values = metadata.get(key, [])
    if not values:
        return None
    if len(values) != 1:
        raise ValueError(f"asset.{key} must appear once in {path}")
    value = values[0]
    if not value:
        raise ValueError(f"asset.{key} must have a value in {path}")
    return value


def reject_duplicates[T](
    items: Iterable[T],
    label: str,
    path: Path,
    key: Callable[[T], object] = lambda item: item,
) -> tuple[T, ...]:
    values: list[T] = []
    seen: set[object] = set()
    for item in items:
        if key(item) in seen:
            raise ValueError(f"Duplicate {label} '{key(item)}' in {path}")
        seen.add(key(item))
        values.append(item)
    return tuple(values)


def parse_dependencies(values: list[str], path: Path) -> tuple[str, ...]:
    dependencies: list[str] = []
    for raw_value in values:
        dependency = parse_metadata_value(
            raw_value, path, "depends", label="dependency"
        )
        validate_asset_reference(dependency, path)
        dependencies.append(dependency)
    return reject_duplicates(dependencies, "dependency", path)


def parse_column_names(values: list[str], path: Path, key: str) -> tuple[str, ...]:
    columns: list[str] = []
    for raw_value in values:
        column = parse_metadata_value(raw_value, path, key, label="column")
        validate_identifier(column, "column", path)
        columns.append(column)
    return reject_duplicates(columns, f"asset.{key} column", path)


def parse_assertions(values: list[str], path: Path) -> tuple[str, ...]:
    if not all(values):
        raise ValueError(f"asset.assert must have a value in {path}")
    return reject_duplicates(values, "asset.assert", path)


def parse_columns(values: list[str], path: Path) -> tuple[AssetColumn, ...]:
    columns: list[AssetColumn] = []
    for raw_value in values:
        name, separator, description = raw_value.partition("|")
        if not separator:
            raise ValueError(
                f"asset.column must use 'name | description' in {path}: {raw_value}"
            )
        column = AssetColumn(name=name.strip(), description=description.strip())
        validate_identifier(column.name, "column", path)
        if not column.description:
            raise ValueError(f"asset.column must include a description in {path}")
        columns.append(column)
    return reject_duplicates(columns, "asset.column", path, key=lambda c: c.name)


def parse_metadata_value(value: str, path: Path, key: str, *, label: str) -> str:
    if not value:
        raise ValueError(f"asset.{key} must have a value in {path}")
    if "," in value:
        raise ValueError(
            f"asset.{key} must declare one {label} per line in {path}: {value}"
        )
    return value


def asset_identity_from_path(path: Path, assets_root: Path) -> tuple[str, str]:
    parts = path.relative_to(assets_root).with_suffix("").parts
    if len(parts) < 2:
        raise ValueError(
            f"Asset path must include a schema folder under assets: {path}"
        )

    schema, *table_parts = parts
    validate_identifier(schema, "schema", path)
    for part in table_parts:
        validate_identifier(part, "table", path)
    return schema, "_".join(table_parts)


def validate_asset_reference(value: str, path: Path) -> None:
    parts = value.split(".")
    if len(parts) != 2:
        raise ValueError(
            f"Invalid dependency '{value}' in {path}. Expected schema.table."
        )
    schema, table = parts
    validate_identifier(schema, "schema", path)
    validate_identifier(table, "table", path)


def validate_identifier(value: str, label: str, path: Path) -> None:
    if IDENTIFIER_RE.fullmatch(value) is None:
        raise ValueError(f"Invalid {label} name '{value}' from {path}")


def parse_asset_runtime(
    kind: AssetKind,
    metadata: dict[str, list[str]],
    path: Path,
) -> AssetRuntime:
    if kind == "python":
        if metadata.get("resource"):
            raise ValueError(f"asset.resource is only supported on SQL assets: {path}")
        return parse_python_materialization(metadata, path)
    if metadata.get("materialization"):
        raise ValueError(
            f"asset.materialization is only supported on Python assets: {path}"
        )
    return parse_sql_resource(metadata, path)


def parse_python_materialization(
    metadata: dict[str, list[str]],
    path: Path,
) -> AssetRuntime:
    materialization = metadata_value(metadata, "materialization", path)
    if materialization is None:
        raise ValueError(f"Python asset {path} must declare asset.materialization")
    runtime = PYTHON_RUNTIME_BY_MATERIALIZATION.get(materialization)
    if runtime is None:
        raise ValueError(
            f"Unsupported asset.materialization '{materialization}' in {path}. "
            "Expected dataframe or custom."
        )
    return runtime


def parse_sql_resource(
    metadata: dict[str, list[str]],
    path: Path,
) -> AssetRuntime:
    resource = metadata_value(metadata, "resource", path)
    if resource is None:
        return "sql"
    runtime = SQL_RUNTIME_BY_RESOURCE.get(resource)
    if runtime is None:
        known_resources = ", ".join(sorted(SQL_RUNTIME_BY_RESOURCE))
        raise ValueError(
            f"Unsupported asset.resource '{resource}' in {path}. "
            f"Expected one of: {known_resources}."
        )
    return runtime


def parse_bool_metadata(
    metadata: dict[str, list[str]],
    key: str,
    path: Path,
) -> bool:
    value = metadata_value(metadata, key, path)
    if value is None:
        return False
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    raise ValueError(f"asset.{key} must be true or false in {path}")


def index_assets(assets: Iterable[Asset]) -> dict[str, Asset]:
    indexed: dict[str, Asset] = {}
    for asset in assets:
        if asset.key in indexed:
            raise ValueError(
                f"Duplicate asset key {asset.key}: "
                f"{indexed[asset.key].path} and {asset.path}"
            )
        indexed[asset.key] = asset
    return indexed


def dependency_graph(assets: dict[str, Asset]) -> dict[str, tuple[str, ...]]:
    graph: dict[str, tuple[str, ...]] = {}
    for asset in assets.values():
        for dependency in asset.depends:
            if dependency == asset.key:
                raise ValueError(f"Asset {asset.key} depends on itself")
            if dependency not in assets:
                raise ValueError(
                    f"Unknown dependency '{dependency}' referenced in {asset.path}"
                )
        graph[asset.key] = tuple(sorted(asset.depends))
    return graph


def topological_order(graph: dict[str, tuple[str, ...]]) -> list[str]:
    try:
        return list(TopologicalSorter(graph).static_order())
    except CycleError as exc:
        raise ValueError(f"Dependency cycle detected: {exc}") from exc


def run_validation_step[T](
    label: str,
    reporter: ValidationReporter,
    func: Callable[[], T],
) -> T:
    try:
        result = func()
    except Exception:
        reporter(label, "FAIL")
        raise
    reporter(label, "OK")
    return result


def print_check_status(label: str, status: str) -> None:
    print(f"{label:.<38} {status}", flush=True)
