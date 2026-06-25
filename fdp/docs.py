import csv
import io
from pathlib import Path

from fdp.api import default_docs_path
from fdp.assets import Asset, load_assets
from fdp.inspect import AssetView, inspect_assets
from fdp.tabular import format_cell

PUBLIC_DATASETS_BASE_URL = "https://data.filecoindataportal.xyz"
GITHUB_BLOB_BASE_URL = "https://github.com/davidgasquez/filecoin-data-portal/blob/main"


def generate_docs(
    out_path: Path | str | None = None,
    sample_rows: int = 10,
) -> None:
    if sample_rows < 1:
        raise ValueError("sample_rows must be at least 1")

    loaded = load_assets()
    asset_keys = [
        key for key in loaded.ordered_keys if loaded.assets[key].schema == "main"
    ]
    if not asset_keys:
        raise ValueError("No main assets found.")

    asset_views = inspect_assets(
        loaded,
        asset_keys=asset_keys,
        require_materialized=True,
        include_row_count=True,
        sample_rows=sample_rows,
    )
    destination = default_docs_path() if out_path is None else Path(out_path)
    write_docs(destination, loaded.project_root, asset_views)


def write_docs(
    out_dir: Path,
    project_root: Path,
    asset_views: list[AssetView],
) -> None:
    documented_asset_filenames = {
        asset_view.asset.key: asset_doc_filename(asset_view.asset)
        for asset_view in asset_views
    }
    assets_dir = out_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    for path in assets_dir.glob("*.md"):
        path.unlink()

    (out_dir / "SKILL.md").write_text(
        render_skill_markdown(asset_views, asset_docs_path="assets"),
        encoding="utf-8",
    )
    for asset_view in asset_views:
        (assets_dir / documented_asset_filenames[asset_view.asset.key]).write_text(
            render_asset_markdown(
                asset_view,
                project_root,
                documented_asset_filenames,
            ),
            encoding="utf-8",
        )


def render_skill_markdown(asset_views: list[AssetView], *, asset_docs_path: str) -> str:
    lines = [
        "---",
        "name: fdp",
        (
            "description: Use when the user asks about Filecoin Data Portal, FDP, "
            "Filecoin parquet datasets, Filecoin clients, storage providers, "
            "network metrics, Filecoin Pay, PDP, or warm storage data."
        ),
        "---",
        "",
        "## Dataset Catalog",
        "",
        *render_dataset_links(asset_views, asset_docs_path=asset_docs_path),
        "",
        "## Workflow",
        "",
        "1. Choose the most relevant datasets from the catalog.",
        "2. Read the dataset docs before querying.",
        "3. Inspect columns, types, and sample rows.",
        "4. Query the canonical parquet URL:",
        f"   `{PUBLIC_DATASETS_BASE_URL}/<dataset>.parquet`",
        "5. Answer with the datasets used and any important caveats.",
        "",
        "Use DuckDB first:",
        "",
        "```sh",
        (
            'duckdb -c "describe select * from read_parquet('
            f"'{PUBLIC_DATASETS_BASE_URL}/<dataset>.parquet'"
            ')"'
        ),
        "```",
        "",
        (
            "Ask a clarification question only if the relevant dataset or metric "
            "remains ambiguous."
        ),
        "",
        "## Charts",
        "",
        "When asked for a chart or dashboard:",
        "",
        "1. Create a self-contained `index.html` with vanilla HTML, CSS, and JS.",
        "2. Mention and link `filecoindataportal.xyz` as the source.",
        "3. Serve it locally and share the URL.",
        "",
    ]
    return "\n".join(lines)


def render_dataset_links(
    asset_views: list[AssetView],
    *,
    asset_docs_path: str,
) -> list[str]:
    lines: list[str] = []
    for asset_view in asset_views:
        description = asset_view.asset.description or "No description."
        lines.append(
            f"- [`{asset_view.asset.name}`]"
            f"({asset_docs_path}/{asset_doc_filename(asset_view.asset)})"
            f" — {description}"
        )
    return lines


def render_asset_markdown(
    asset_view: AssetView,
    project_root: Path,
    documented_asset_filenames: dict[str, str],
) -> str:
    asset = asset_view.asset
    description = asset.description or "_No description._"
    asset_path = asset.path.relative_to(project_root).as_posix()
    asset_code_url = f"{GITHUB_BLOB_BASE_URL}/{asset_path}"
    dataset_url = public_dataset_url(asset)
    lines = [
        f"# {asset.key}",
        "",
        description,
        "",
        f"- asset code: `{asset_code_url}`",
        f"- dataset url: `{dataset_url}`",
        f"- rows: `{asset_view.row_count}`",
    ]
    if asset.depends:
        lines.extend([
            "",
            "## Depends",
            "",
            *render_dependencies(asset_view, documented_asset_filenames),
        ])
    lines.extend([
        "",
        "## Columns",
        "",
        render_columns_table(asset_view),
        "",
        "## Sample",
        "",
        render_sample_csv(asset_view.sample_columns, asset_view.sample_rows),
        "",
    ])
    return "\n".join(lines)


def public_dataset_url(asset: Asset) -> str:
    return f"{PUBLIC_DATASETS_BASE_URL}/{asset.name}.parquet"


def render_dependencies(
    asset_view: AssetView,
    documented_asset_filenames: dict[str, str],
) -> list[str]:
    return [
        (
            f"- [`{dependency}`]({documented_asset_filenames[dependency]})"
            if dependency in documented_asset_filenames
            else f"- `{dependency}`"
        )
        for dependency in asset_view.asset.depends
    ]


def asset_doc_filename(asset: Asset) -> str:
    return f"{asset.name}.md"


def render_columns_table(asset_view: AssetView) -> str:
    asset = asset_view.asset
    if not asset.columns:
        return "_No documented columns._"

    types_by_column = {column.name: column.data_type for column in asset_view.columns}
    tests_by_column = column_tests(asset_view)
    lines = [
        "| column | type | description | tests |",
        "|---|---|---|---|",
    ]
    for column in asset.columns:
        tests = ", ".join(f"`{test}`" for test in tests_by_column.get(column.name, []))
        lines.append(
            "| "
            f"`{escape_markdown(column.name)}` | "
            f"`{escape_markdown(types_by_column[column.name])}` | "
            f"{escape_markdown(column.description)} | "
            f"{tests} |"
        )
    return "\n".join(lines)


def render_sample_csv(
    columns: tuple[str, ...],
    rows: tuple[tuple[object, ...], ...],
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


def column_tests(asset_view: AssetView) -> dict[str, list[str]]:
    tests: dict[str, list[str]] = {}
    for column in asset_view.asset.tests.not_null:
        tests.setdefault(column, []).append("not_null")
    for column in asset_view.asset.tests.unique:
        tests.setdefault(column, []).append("unique")
    return tests


def escape_markdown(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
