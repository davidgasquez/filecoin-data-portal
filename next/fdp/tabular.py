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
    if not columns:
        return ["no columns"]
    if not rows:
        return ["no rows"]

    rendered_rows = [
        [format_cell(value, lowercase_bools=lowercase_bools) for value in row]
        for row in rows
    ]
    widths = [len(column) for column in columns]
    for row in rendered_rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    header = " | ".join(
        column.ljust(widths[index]) for index, column in enumerate(columns)
    )
    divider = "-+-".join("-" * width for width in widths)
    body = [
        " | ".join(value.ljust(widths[index]) for index, value in enumerate(row))
        for row in rendered_rows
    ]
    return [header, divider, *body]
