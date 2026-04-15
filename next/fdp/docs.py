import csv
import io
from pathlib import Path

from fdp.api import default_docs_path
from fdp.assets import Asset, load_assets
from fdp.inspect import AssetView, inspect_assets
from fdp.tabular import format_cell

PUBLIC_DATASETS_BASE_URL = "https://data.filecoindataportal.xyz"
GITHUB_TREE_BASE_URL = (
    "https://github.com/davidgasquez/filecoin-data-portal/tree/main/next"
)


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
        "## Datasets",
        "",
        *render_dataset_links(asset_views, asset_docs_path=asset_docs_path),
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
        "- Clone the repo for deeper exploration if needed.",
        "",
        "## Charts & Dashboards",
        "",
        "When the user asks for a chart, dashboard, or visualization:",
        "",
        "1. Write a self-contained `index.html` using vanilla HTML, CSS, and JS.",
        "2. Serve it locally and share the URL.",
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
    asset_code_url = f"{GITHUB_TREE_BASE_URL}/{asset_path}"
    lines = [
        f"# {asset.key}",
        "",
        description,
        "",
        f"- asset code: `{asset_code_url}`",
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
        "## Tests",
        "",
        *render_tests(asset_view, project_root),
        "",
        "## Columns",
        "",
        render_columns_table(asset_view),
        "",
        f"## Sample ({len(asset_view.sample_rows)} rows)",
        "",
        render_sample_csv(asset_view.sample_columns, asset_view.sample_rows),
        "",
    ])
    return "\n".join(lines)


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


def render_tests(asset_view: AssetView, project_root: Path) -> list[str]:
    asset = asset_view.asset
    lines = [
        *(f"- `not_null({column})`" for column in asset.tests.not_null),
        *(f"- `unique({column})`" for column in asset.tests.unique),
        *(f"- `assert({assertion})`" for assertion in asset.tests.assertions),
    ]
    for custom_test in asset_view.custom_tests:
        lines.append(
            f"- `custom({custom_test.path.relative_to(project_root).as_posix()})`"
        )
    if not lines:
        return ["- none"]
    return lines


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
