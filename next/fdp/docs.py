import csv
import io
from dataclasses import dataclass
from pathlib import Path

from fdp.api import db_connection, find_assets_root, table_exists
from fdp.assets import Asset, main_assets
from fdp.test import custom_test_paths_for_asset, format_cell

PUBLIC_DATASETS_BASE_URL = "https://data.filecoindataportal.xyz"


@dataclass(frozen=True)
class AssetDoc:
    asset: Asset
    columns: list[tuple[str, str]]
    row_count: int
    sample_columns: list[str]
    sample_rows: list[tuple[object, ...]]


def generate_docs(out_path: Path | str, sample_rows: int = 10) -> None:
    if sample_rows < 1:
        raise ValueError("sample_rows must be at least 1")

    out_dir = Path(out_path)
    assets_root = find_assets_root()
    assets = main_assets(assets_root=assets_root)
    if not assets:
        raise ValueError("No main assets found.")

    asset_docs = collect_asset_docs(assets, sample_rows)
    write_docs(out_dir, assets_root, asset_docs)


def collect_asset_docs(assets: list[Asset], sample_rows: int) -> list[AssetDoc]:
    asset_docs: list[AssetDoc] = []
    with db_connection(read_only=True) as conn:
        for asset in assets:
            if not table_exists(conn, asset.schema, asset.name):
                raise ValueError(f"Missing table {asset.key}. Run `fdp materialize`.")
            sample_cursor = conn.execute(
                f"select * from {asset.key} limit {sample_rows}"
            )
            sample_values = sample_cursor.fetchall()
            sample_columns = [
                description[0] for description in sample_cursor.description
            ]
            row_count = conn.execute(f"select count(*) from {asset.key}").fetchone()
            if row_count is None:
                raise ValueError(f"Missing count for {asset.key}")
            asset_docs.append(
                AssetDoc(
                    asset=asset,
                    columns=conn.execute(
                        "select column_name, data_type "
                        "from information_schema.columns "
                        "where table_schema = ? and table_name = ? "
                        "order by ordinal_position",
                        [asset.schema, asset.name],
                    ).fetchall(),
                    row_count=int(row_count[0]),
                    sample_columns=sample_columns,
                    sample_rows=sample_values,
                )
            )
    return asset_docs


def write_docs(out_dir: Path, assets_root: Path, asset_docs: list[AssetDoc]) -> None:
    documented_asset_keys = {asset_doc.asset.key for asset_doc in asset_docs}
    assets_dir = out_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    for path in assets_dir.glob("*.md"):
        path.unlink()

    (out_dir / "index.md").write_text(
        render_index_markdown(asset_docs),
        encoding="utf-8",
    )
    (out_dir / "SKILL.md").write_text(
        render_skill_markdown(asset_docs, asset_docs_path="assets"),
        encoding="utf-8",
    )
    for asset_doc in asset_docs:
        (assets_dir / f"{asset_doc.asset.key}.md").write_text(
            render_asset_markdown(
                asset_doc,
                assets_root,
                documented_asset_keys,
            ),
            encoding="utf-8",
        )


def render_index_markdown(asset_docs: list[AssetDoc]) -> str:
    lines = [
        "# FDP catalog",
        "",
        "Generated from `assets/main/` and materialized DuckDB main tables.",
        "",
        *render_dataset_links(asset_docs, asset_docs_path="assets"),
        "",
    ]
    return "\n".join(lines)


def render_skill_markdown(asset_docs: list[AssetDoc], *, asset_docs_path: str) -> str:
    lines = [
        "---",
        "name: fdp",
        "description: Help users explore and use Filecoin Data Portal (fdp) datasets.",
        "---",
        "",
        "# Filecoin Data Portal",
        "",
        (
            "Guidelines on how to help users explore and use Filecoin Data Portal "
            "(fdp) datasets."
        ),
        "",
        "Generated from `assets/main/` and materialized DuckDB main tables.",
        "",
        "## Datasets",
        "",
        *render_dataset_links(asset_docs, asset_docs_path=asset_docs_path),
        "",
        "## Using Datasets",
        "",
        (
            "Start with `duckdb` if available. Consider asking the user to "
            "install it or ask the user for a tool (Pandas, Javascript, ...) "
            "to use as a replacement."
        ),
        "",
        (
            "Canonical dataset URLs follow "
            f"`{PUBLIC_DATASETS_BASE_URL}/<dataset>.parquet`."
        ),
        "",
        "1. Inspect the dataset.",
        "2. Read the columns, types, and a few sample rows.",
        "3. Ask any clarification question if needed.",
        "4. Write temporary self-contained scripts that answer the user's question.",
        "5. Get back in a clear and concise way.",
        "",
        "## Answering Questions",
        "",
        "- Mention the used datasets explicitly.",
        "- Inspect columns, types, and sample rows first.",
        "- Offer to plot charts if it makes sense.",
        "",
    ]
    return "\n".join(lines)


def render_dataset_links(
    asset_docs: list[AssetDoc],
    *,
    asset_docs_path: str,
) -> list[str]:
    lines: list[str] = []
    for asset_doc in asset_docs:
        description = asset_doc.asset.description or "No description."
        lines.append(
            f"- [`{asset_doc.asset.name}`]"
            f"({asset_docs_path}/{asset_doc.asset.key}.md)"
            f" — {description}"
        )
    return lines


def render_asset_markdown(
    asset_doc: AssetDoc,
    assets_root: Path,
    documented_asset_keys: set[str],
) -> str:
    asset = asset_doc.asset
    project_root = assets_root.parent
    relative_path = asset.path.relative_to(project_root).as_posix()
    description = asset.description or "_No description._"
    lines = [
        f"# {asset.key}",
        "",
        description,
        "",
        f"- path: `{relative_path}`",
        f"- rows: `{asset_doc.row_count}`",
    ]
    if asset.depends:
        lines.extend([
            "",
            "## Depends",
            "",
            *render_dependencies(asset, documented_asset_keys),
        ])
    lines.extend([
        "",
        "## Tests",
        "",
        *render_tests(asset, assets_root),
        "",
        "## Columns",
        "",
        render_columns_table(asset_doc.columns, asset),
        "",
        f"## Sample ({len(asset_doc.sample_rows)} rows)",
        "",
        render_sample_csv(asset_doc.sample_columns, asset_doc.sample_rows),
        "",
    ])
    return "\n".join(lines)


def render_dependencies(asset: Asset, documented_asset_keys: set[str]) -> list[str]:
    return [
        (
            f"- [`{dependency}`]({dependency}.md)"
            if dependency in documented_asset_keys
            else f"- `{dependency}`"
        )
        for dependency in asset.depends
    ]


def render_tests(asset: Asset, assets_root: Path) -> list[str]:
    project_root = assets_root.parent
    lines = [
        *(f"- `not_null({column})`" for column in asset.tests.not_null),
        *(f"- `unique({column})`" for column in asset.tests.unique),
        *(f"- `assert({assertion})`" for assertion in asset.tests.assertions),
    ]
    for path in custom_test_paths_for_asset(asset, assets_root):
        lines.append(f"- `custom({path.relative_to(project_root).as_posix()})`")
    if not lines:
        return ["- none"]
    return lines


def render_columns_table(columns: list[tuple[str, str]], asset: Asset) -> str:
    if not columns:
        return "_No columns._"

    descriptions = {column.name: column.description for column in asset.columns}
    tests_by_column = column_tests(asset)
    lines = [
        "| column | type | description | tests |",
        "|---|---|---|---|",
    ]
    for name, data_type in columns:
        tests = ", ".join(f"`{test}`" for test in tests_by_column.get(name, []))
        lines.append(
            "| "
            f"`{escape_markdown(name)}` | "
            f"`{escape_markdown(data_type)}` | "
            f"{escape_markdown(descriptions.get(name, ''))} | "
            f"{tests} |"
        )
    return "\n".join(lines)


def render_sample_csv(
    columns: list[str],
    rows: list[tuple[object, ...]],
) -> str:
    if not columns:
        return "_No sample available._"
    if not rows:
        return "_No rows._"

    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(columns)
    for row in rows:
        writer.writerow([format_cell(value) for value in row])
    content = buffer.getvalue().rstrip()
    return "\n".join(["```csv", content, "```"])


def column_tests(asset: Asset) -> dict[str, list[str]]:
    tests: dict[str, list[str]] = {}
    for column in asset.tests.not_null:
        tests.setdefault(column, []).append("not_null")
    for column in asset.tests.unique:
        tests.setdefault(column, []).append("unique")
    return tests


def escape_markdown(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
