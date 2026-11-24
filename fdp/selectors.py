from pathlib import Path

from fdp.assets import LoadedAssets


def expand_asset_selectors(loaded: LoadedAssets, selectors: list[str]) -> list[str]:
    if not selectors:
        return []

    exact_index = asset_exact_selector_index(loaded)
    folder_index = asset_folder_index(loaded)
    selected: dict[str, None] = {}
    unknown_selectors: list[str] = []

    for raw_selector in selectors:
        candidates = selector_candidates(raw_selector)
        exact_matches = list(
            dict.fromkeys(exact_index[c] for c in candidates if c in exact_index)
        )
        folder_matches = list(
            dict.fromkeys(key for c in candidates for key in folder_index.get(c, ()))
        )

        if len(exact_matches) > 1:
            raise ValueError(
                f"Ambiguous selector '{raw_selector}': matches multiple assets"
            )
        if exact_matches and folder_matches:
            raise ValueError(
                f"Ambiguous selector '{raw_selector}': matches both an asset "
                "and an asset folder"
            )
        if not (exact_matches or folder_matches):
            unknown_selectors.append(raw_selector)
            continue

        selected.update(dict.fromkeys(exact_matches or folder_matches))

    if unknown_selectors:
        raise ValueError(f"Unknown selectors: {', '.join(sorted(unknown_selectors))}")

    return list(selected)


def selector_candidates(raw_selector: str) -> list[str]:
    candidates = [Path(raw_selector).as_posix()]
    if is_path_selector(raw_selector):
        candidates.append(Path(raw_selector).expanduser().resolve().as_posix())
    return candidates


def is_path_selector(selector: str) -> bool:
    return (
        "/" in selector
        or "\\" in selector
        or selector.startswith(".")
        or selector.endswith((".py", ".sql"))
    )


def asset_exact_selector_index(loaded: LoadedAssets) -> dict[str, str]:
    exact_index: dict[str, str] = {}
    for asset in loaded.assets.values():
        for selector in (
            asset.key,
            asset.path.relative_to(loaded.assets_root).as_posix(),
            asset.path.relative_to(loaded.project_root).as_posix(),
            asset.path.as_posix(),
        ):
            existing = exact_index.setdefault(selector, asset.key)
            if existing != asset.key:
                raise ValueError(
                    f"Duplicate selector '{selector}' for assets {existing} and "
                    f"{asset.key}"
                )
    return exact_index


def asset_folder_index(loaded: LoadedAssets) -> dict[str, tuple[str, ...]]:
    folder_index: dict[str, set[str]] = {}
    for asset in loaded.assets.values():
        parts = asset.path.parent.relative_to(loaded.project_root).parts
        for index in range(1, len(parts) + 1):
            prefix = Path(*parts[:index])
            selectors = [prefix.as_posix(), (loaded.project_root / prefix).as_posix()]
            if index > 1:
                schema = parts[1:index]
                selectors += [Path(*schema).as_posix(), ".".join(schema)]
            for selector in selectors:
                folder_index.setdefault(selector, set()).add(asset.key)
    return {
        selector: tuple(sorted(asset_keys))
        for selector, asset_keys in folder_index.items()
    }
