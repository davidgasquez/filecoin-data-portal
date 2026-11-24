def format_cell(value: object, *, lowercase_bools: bool = False) -> str:
    if value is None:
        return "null"
    if lowercase_bools and isinstance(value, bool):
        return str(value).lower()
    return str(value)


def render_text_table(
    columns: list[str] | tuple[str, ...],
    rows: list[tuple[object, ...]] | tuple[tuple[object, ...], ...],
    *,
    lowercase_bools: bool = False,
) -> list[str]:
    if not rows:
        return ["no rows"]

    cells = [
        [format_cell(v, lowercase_bools=lowercase_bools) for v in row] for row in rows
    ]
    widths = [max(map(len, column)) for column in zip(columns, *cells, strict=True)]

    def line(values: list[str] | tuple[str, ...]) -> str:
        return " | ".join(v.ljust(w) for v, w in zip(values, widths, strict=True))

    return [line(columns), "-+-".join("-" * w for w in widths), *map(line, cells)]
