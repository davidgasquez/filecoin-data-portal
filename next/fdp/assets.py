import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from graphlib import CycleError, TopologicalSorter
from pathlib import Path
from typing import Literal

from fdp.api import find_assets_root

AssetKind = Literal["python", "sql"]
PythonMaterialization = Literal["dataframe", "custom"]
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
}
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
METADATA_LINE_RE = re.compile(
    r"asset\.(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)"
)

PARSE_ASSETS_LABEL = "parse asset files and metadata"
UNIQUE_ASSET_KEYS_LABEL = "validate unique asset keys"
METADATA_MODEL_LABEL = "validate metadata model"
DEPENDENCIES_LABEL = "validate dependencies"
CUSTOM_SQL_TESTS_LABEL = "parse custom sql tests"
DEPENDENCY_ORDERING_LABEL = "validate dependency ordering"
CHECK_STATUS_WIDTH = (
    max(
        len(PARSE_ASSETS_LABEL),
        len(UNIQUE_ASSET_KEYS_LABEL),
        len(METADATA_MODEL_LABEL),
        len(DEPENDENCIES_LABEL),
        len(CUSTOM_SQL_TESTS_LABEL),
        len(DEPENDENCY_ORDERING_LABEL),
    )
    + 8
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
    asset_key: str
    name: str
    path: Path


@dataclass(frozen=True)
class Asset:
    name: str
    schema: str
    key: str
    path: Path
    kind: AssetKind
    python_materialization: PythonMaterialization | None
    depends: tuple[str, ...]
    description: str | None
    columns: tuple[AssetColumn, ...]
    tests: AssetTests


@dataclass(frozen=True)
class LoadedAssets:
    root: Path
    assets: dict[str, Asset]
    graph: dict[str, tuple[str, ...]]
    ordered_keys: tuple[str, ...]
    custom_tests_by_asset: dict[str, tuple[CustomSqlTest, ...]]


def load_assets(
    names: Iterable[str] | None = None,
    *,
    assets_root: Path | None = None,
    reporter: ValidationReporter | None = None,
    include_dependencies: bool = True,
) -> LoadedAssets:
    requested_names = None if names is None else list(names)
    root = assets_root or find_assets_root()
    asset_list = run_validation_step(
        PARSE_ASSETS_LABEL,
        reporter,
        lambda: collect_assets(root),
    )
    assets = run_validation_step(
        UNIQUE_ASSET_KEYS_LABEL,
        reporter,
        lambda: index_assets(asset_list),
    )
    run_validation_step(
        METADATA_MODEL_LABEL,
        reporter,
        lambda: validate_metadata_model(asset_list),
    )
    graph = run_validation_step(
        DEPENDENCIES_LABEL,
        reporter,
        lambda: dependency_graph(assets),
    )
    custom_tests_by_asset = run_validation_step(
        CUSTOM_SQL_TESTS_LABEL,
        reporter,
        lambda: collect_custom_sql_tests(root, assets),
    )
    selected_keys = tuple(
        sorted(
            resolve_selection(
                requested_names,
                assets,
                graph,
                include_dependencies=include_dependencies,
            )
        )
    )
    ordered_keys = tuple(
        run_validation_step(
            DEPENDENCY_ORDERING_LABEL,
            reporter,
            lambda: topological_order(selected_graph(graph, selected_keys)),
        )
    )
    return LoadedAssets(
        root=root,
        assets=assets,
        graph=graph,
        ordered_keys=ordered_keys,
        custom_tests_by_asset=custom_tests_by_asset,
    )


def check_assets() -> None:
    load_assets(reporter=print_check_status)


def discover_assets(assets_root: Path) -> dict[str, Asset]:
    return load_assets(assets_root=assets_root).assets


def schema_assets(
    schema: str,
    *,
    assets_root: Path | None = None,
) -> list[Asset]:
    root = assets_root or find_assets_root()
    assets = discover_assets(root)
    return sorted(
        (asset for asset in assets.values() if asset.schema == schema),
        key=lambda asset: asset.key,
    )


def main_assets(*, assets_root: Path | None = None) -> list[Asset]:
    return schema_assets("main", assets_root=assets_root)


def ordered_assets(
    names: Iterable[str] | None = None,
    reporter: ValidationReporter | None = None,
    *,
    include_dependencies: bool = True,
) -> list[Asset]:
    loaded = load_assets(
        names,
        reporter=reporter,
        include_dependencies=include_dependencies,
    )
    return [loaded.assets[key] for key in loaded.ordered_keys]


def collect_assets(assets_root: Path) -> list[Asset]:
    return [asset_from_path(path, assets_root) for path in asset_files(assets_root)]


def asset_files(assets_root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in assets_root.rglob("*"):
        if not path.is_file():
            continue
        if path.name.startswith("_"):
            continue
        if "__pycache__" in path.parts:
            continue
        if path.suffix not in ASSET_KIND_BY_SUFFIX:
            continue
        if path.name.endswith(".test.sql"):
            continue
        paths.append(path)
    return sorted(paths)


def custom_sql_test_files(assets_root: Path) -> list[Path]:
    return sorted(assets_root.rglob("*.test.sql"))


def validate_metadata_model(assets: Iterable[Asset]) -> None:
    for asset in assets:
        if asset.schema != "main":
            continue
        if asset.columns:
            continue
        raise ValueError(
            f"Main asset {asset.key} must define asset.column metadata in {asset.path}"
        )


def collect_custom_sql_tests(
    assets_root: Path,
    assets: dict[str, Asset],
) -> dict[str, tuple[CustomSqlTest, ...]]:
    tests_by_asset = {asset_key: [] for asset_key in assets}
    for path in custom_sql_test_files(assets_root):
        asset_key, test_name = custom_sql_test_identity(path, assets_root)
        if asset_key not in assets:
            raise ValueError(f"Unknown asset '{asset_key}' referenced in {path}")
        tests_by_asset[asset_key].append(
            CustomSqlTest(asset_key=asset_key, name=test_name, path=path)
        )
    return {asset_key: tuple(tests) for asset_key, tests in tests_by_asset.items()}


def custom_sql_test_identity(path: Path, assets_root: Path) -> tuple[str, str]:
    relative_path = path.relative_to(assets_root)
    if len(relative_path.parts) < 2:
        raise ValueError(
            f"Data test path must include a schema folder under assets: {path}"
        )

    schema = relative_path.parts[0]
    validate_identifier(schema, "schema", path)
    asset_name, separator, test_name = path.name.removesuffix(".test.sql").partition(
        "__"
    )
    if not separator or not test_name:
        raise ValueError(
            f"Invalid data test file name '{path}'. Expected asset__name.test.sql"
        )

    validate_identifier(asset_name, "table", path)
    validate_identifier(test_name, "test", path)
    asset_key = f"{schema}.{asset_name}"
    validate_asset_reference(asset_key, path)
    return asset_key, test_name


def read_custom_sql_test_query(path: Path) -> str:
    query = path.read_text(encoding="utf-8").strip()
    if not query:
        raise ValueError(f"Data test file is empty: {path}")
    if query.endswith(";"):
        return query[:-1].rstrip()
    return query


def asset_from_path(path: Path, assets_root: Path) -> Asset:
    kind = asset_kind_from_path(path)
    source = path.read_text(encoding="utf-8")
    metadata, body_lines = metadata_from_source(path, kind, source)
    ensure_asset_body(body_lines, path)
    schema, name = asset_identity_from_path(path, assets_root)
    python_materialization = parse_python_materialization(kind, metadata, path)

    return Asset(
        name=name,
        schema=schema,
        key=f"{schema}.{name}",
        path=path,
        kind=kind,
        python_materialization=python_materialization,
        depends=tuple(parse_dependencies(metadata.get("depends", []), path)),
        description=optional_metadata_value(metadata, "description", path),
        columns=tuple(parse_columns(metadata.get("column", []), path)),
        tests=AssetTests(
            not_null=tuple(
                parse_column_names(metadata.get("not_null", []), path, "not_null")
            ),
            unique=tuple(
                parse_column_names(metadata.get("unique", []), path, "unique")
            ),
            assertions=tuple(parse_assertions(metadata.get("assert", []), path)),
        ),
    )


def asset_kind_from_path(path: Path) -> AssetKind:
    try:
        return ASSET_KIND_BY_SUFFIX[path.suffix]
    except KeyError as exc:
        raise ValueError(f"Unsupported asset type: {path}") from exc


def metadata_from_source(
    path: Path,
    kind: AssetKind,
    source: str,
) -> tuple[dict[str, list[str]], list[str]]:
    prefix = COMMENT_PREFIXES[kind]
    metadata_lines, body_lines = extract_metadata_lines(source, prefix)
    return parse_metadata_lines(metadata_lines, path), body_lines


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

        current_values = metadata[current_key]
        current_values[-1] = append_metadata_continuation(current_values[-1], line)

    return metadata


def append_metadata_continuation(value: str, continuation: str) -> str:
    continuation = continuation.strip()
    if not continuation:
        return value
    if not value:
        return continuation
    return f"{value} {continuation}"


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


def optional_metadata_value(
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


def parse_dependencies(values: list[str], path: Path) -> list[str]:
    dependencies: list[str] = []
    seen: set[str] = set()
    for raw_value in values:
        dependency = parse_metadata_value(
            raw_value, path, "depends", label="dependency"
        )
        validate_asset_reference(dependency, path)
        if dependency in seen:
            raise ValueError(f"Duplicate dependency '{dependency}' in {path}")
        seen.add(dependency)
        dependencies.append(dependency)
    return dependencies


def parse_column_names(values: list[str], path: Path, key: str) -> list[str]:
    columns: list[str] = []
    seen: set[str] = set()
    for raw_value in values:
        column = parse_metadata_value(raw_value, path, key, label="column")
        validate_identifier(column, "column", path)
        if column in seen:
            raise ValueError(f"Duplicate asset.{key} column '{column}' in {path}")
        seen.add(column)
        columns.append(column)
    return columns


def parse_assertions(values: list[str], path: Path) -> list[str]:
    assertions: list[str] = []
    seen: set[str] = set()
    for raw_value in values:
        assertion = raw_value.strip()
        if not assertion:
            raise ValueError(f"asset.assert must have a value in {path}")
        if assertion in seen:
            raise ValueError(f"Duplicate asset.assert '{assertion}' in {path}")
        seen.add(assertion)
        assertions.append(assertion)
    return assertions


def parse_columns(values: list[str], path: Path) -> list[AssetColumn]:
    columns: list[AssetColumn] = []
    seen: set[str] = set()
    for raw_value in values:
        name, separator, description = raw_value.partition("|")
        if not separator:
            raise ValueError(
                f"asset.column must use 'name | description' in {path}: {raw_value}"
            )
        column_name = name.strip()
        column_description = description.strip()
        validate_identifier(column_name, "column", path)
        if not column_description:
            raise ValueError(f"asset.column must include a description in {path}")
        if column_name in seen:
            raise ValueError(f"Duplicate asset.column '{column_name}' in {path}")
        seen.add(column_name)
        columns.append(AssetColumn(name=column_name, description=column_description))
    return columns


def parse_metadata_value(raw_value: str, path: Path, key: str, *, label: str) -> str:
    value = raw_value.strip()
    if not value:
        raise ValueError(f"asset.{key} must have a value in {path}")
    if "," in value:
        raise ValueError(
            f"asset.{key} must declare one {label} per line in {path}: {value}"
        )
    return value


def ensure_asset_body(body_lines: list[str], path: Path) -> None:
    if any(line.strip() for line in body_lines):
        return
    raise ValueError(f"Asset file has no content beyond metadata: {path}")


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


def parse_python_materialization(
    kind: AssetKind,
    metadata: dict[str, list[str]],
    path: Path,
) -> PythonMaterialization | None:
    values = metadata.get("materialization", [])
    if kind != "python":
        if values:
            raise ValueError(
                f"asset.materialization is only supported on Python assets: {path}"
            )
        return None

    if not values:
        raise ValueError(f"Python asset {path} must declare asset.materialization")
    if len(values) != 1:
        raise ValueError(f"asset.materialization must appear once in {path}")

    materialization = values[0].strip()
    if not materialization:
        raise ValueError(f"asset.materialization must have a value in {path}")
    if materialization == "dataframe":
        return "dataframe"
    if materialization == "custom":
        return "custom"
    raise ValueError(
        f"Unsupported asset.materialization '{materialization}' in {path}. "
        "Expected dataframe or custom."
    )


def python_asset_function_name(path: Path) -> str:
    return path.stem


def index_assets(assets: Iterable[Asset]) -> dict[str, Asset]:
    indexed: dict[str, Asset] = {}
    for asset in assets:
        if asset.key in indexed:
            raise ValueError(f"Duplicate asset key: {asset.key}")
        indexed[asset.key] = asset
    return indexed


def dependency_graph(assets: dict[str, Asset]) -> dict[str, tuple[str, ...]]:
    graph: dict[str, tuple[str, ...]] = {}
    asset_keys = set(assets)
    for asset in assets.values():
        for dependency in asset.depends:
            if dependency == asset.key:
                raise ValueError(f"Asset {asset.key} depends on itself")
            if dependency not in asset_keys:
                raise ValueError(
                    f"Unknown dependency '{dependency}' referenced in {asset.path}"
                )
        graph[asset.key] = tuple(sorted(asset.depends))
    return graph


def resolve_selection(
    names: Iterable[str] | None,
    assets: dict[str, Asset],
    graph: dict[str, tuple[str, ...]],
    *,
    include_dependencies: bool = True,
) -> set[str]:
    if not names:
        selected = set(assets)
    else:
        unknown = sorted(set(names) - set(assets))
        if unknown:
            raise ValueError(f"Unknown assets: {', '.join(unknown)}")
        selected = set(names)

    if not include_dependencies:
        return selected

    stack = list(selected)
    while stack:
        key = stack.pop()
        for dependency in graph[key]:
            if dependency in selected:
                continue
            selected.add(dependency)
            stack.append(dependency)
    return selected


def selected_graph(
    graph: dict[str, tuple[str, ...]],
    selected_keys: Iterable[str],
) -> dict[str, tuple[str, ...]]:
    ordered_selected = tuple(selected_keys)
    selected = set(ordered_selected)
    return {
        key: tuple(dependency for dependency in graph[key] if dependency in selected)
        for key in ordered_selected
    }


def topological_order(graph: dict[str, tuple[str, ...]]) -> list[str]:
    try:
        return list(TopologicalSorter(graph).static_order())
    except CycleError as exc:
        raise ValueError(f"Dependency cycle detected: {exc}") from exc


def run_validation_step[T](
    label: str,
    reporter: ValidationReporter | None,
    func: Callable[[], T],
) -> T:
    try:
        result = func()
    except Exception:
        report_validation_status(reporter, label, "FAIL")
        raise
    report_validation_status(reporter, label, "OK")
    return result


def report_validation_status(
    reporter: ValidationReporter | None,
    label: str,
    status: str,
) -> None:
    if reporter is not None:
        reporter(label, status)


def print_check_status(label: str, status: str) -> None:
    print(format_check_status(label, status), flush=True)


def format_check_status(label: str, status: str) -> str:
    return f"{label:.<{CHECK_STATUS_WIDTH}} {status}"
