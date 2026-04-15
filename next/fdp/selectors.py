from pathlib import Path

from fdp.assets import LoadedAssets, load_assets


def expand_asset_selectors(
    selectors: list[str] | None,
) -> list[str] | None:
    if not selectors:
        return selectors

    loaded = load_assets()
    exact_index = asset_exact_selector_index(loaded)
    folder_index = asset_folder_index(loaded)
    selected_keys: list[str] = []
    seen: set[str] = set()
    unknown_selectors: list[str] = []

    for raw_selector in selectors:
        exact_matches, folder_matches = selector_matches(
            raw_selector,
            exact_index,
            folder_index,
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

        if exact_matches:
            matched_keys = exact_matches
        elif folder_matches:
            matched_keys = folder_matches
        else:
            unknown_selectors.append(raw_selector)
            continue

        for key in matched_keys:
            if key in seen:
                continue
            seen.add(key)
            selected_keys.append(key)

    if unknown_selectors:
        raise ValueError(f"Unknown selectors: {', '.join(sorted(unknown_selectors))}")

    return selected_keys


def selector_matches(
    raw_selector: str,
    exact_index: dict[str, str],
    folder_index: dict[str, tuple[str, ...]],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    exact_matches: list[str] = []
    seen_exact: set[str] = set()
    folder_matches: list[str] = []
    seen_folder: set[str] = set()

    for candidate in selector_candidates(raw_selector):
        exact_match = exact_index.get(candidate)
        if exact_match is not None and exact_match not in seen_exact:
            seen_exact.add(exact_match)
            exact_matches.append(exact_match)

        for key in folder_index.get(candidate, ()):
            if key in seen_folder:
                continue
            seen_folder.add(key)
            folder_matches.append(key)

    return tuple(exact_matches), tuple(folder_matches)


def selector_candidates(raw_selector: str) -> tuple[str, ...]:
    candidates = [Path(raw_selector).as_posix()]
    if is_path_selector(raw_selector):
        candidates.append(
            Path(raw_selector).expanduser().resolve(strict=False).as_posix()
        )
    return tuple(dict.fromkeys(candidates))


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
        for selector in asset_exact_selectors(asset.key, asset.path, loaded):
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
        relative_path = asset.path.relative_to(loaded.assets_root)
        project_relative_path = asset.path.relative_to(loaded.project_root)
        for selector in (
            *folder_selectors(relative_path.parent),
            *path_selectors(relative_path.parent),
            *path_selectors(project_relative_path.parent),
            *prefixed_path_selectors(loaded.project_root, project_relative_path.parent),
        ):
            folder_index.setdefault(selector, set()).add(asset.key)
    return {
        selector: tuple(sorted(asset_keys))
        for selector, asset_keys in folder_index.items()
    }


def asset_exact_selectors(
    asset_key: str,
    path: Path,
    loaded: LoadedAssets,
) -> tuple[str, ...]:
    selectors = [
        asset_key,
        path.relative_to(loaded.assets_root).as_posix(),
        path.relative_to(loaded.project_root).as_posix(),
        path.as_posix(),
    ]
    return tuple(dict.fromkeys(selectors))


def folder_selectors(path: Path) -> tuple[str, ...]:
    selectors: list[str] = []
    for index in range(1, len(path.parts) + 1):
        selectors.append(".".join(path.parts[:index]))
    return tuple(selectors)


def path_selectors(path: Path) -> tuple[str, ...]:
    selectors: list[str] = []
    for index in range(1, len(path.parts) + 1):
        selectors.append(Path(*path.parts[:index]).as_posix())
    return tuple(selectors)


def prefixed_path_selectors(prefix: Path, path: Path) -> tuple[str, ...]:
    selectors: list[str] = []
    for index in range(1, len(path.parts) + 1):
        selectors.append((prefix / Path(*path.parts[:index])).as_posix())
    return tuple(selectors)
