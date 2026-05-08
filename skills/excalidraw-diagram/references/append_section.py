#!/usr/bin/env python3
"""Append a new section's elements into an existing .excalidraw file.

Handles automatic seed-namespacing and ID collision renaming so that
diagrams can be built incrementally, section-by-section, without
having to hand-merge JSON arrays.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def _die(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def _load_json(path: Path):
    if not path.exists():
        _die(f"file not found: {path}")
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        _die(f"invalid JSON in {path}: {exc}")
    except OSError as exc:
        _die(f"could not read {path}: {exc}")


def _validate_base(data) -> list:
    if not isinstance(data, dict):
        _die("base file must be a JSON object (Excalidraw v2 wrapper)")
    if "elements" not in data:
        _die("base file is missing 'elements' array")
    elements = data["elements"]
    if not isinstance(elements, list):
        _die("base 'elements' must be an array")
    for i, el in enumerate(elements):
        if not isinstance(el, dict):
            _die(f"base element at index {i} is not an object")
    return elements


def _validate_section(data) -> list:
    if not isinstance(data, list):
        _die("section file must be a JSON array of element objects")
    for i, el in enumerate(data):
        if not isinstance(el, dict):
            _die(f"section element at index {i} is not an object")
    return data


def _compute_seed_offset(base_elements: list) -> int:
    max_seed = 0
    for el in base_elements:
        seed = el.get("seed")
        if isinstance(seed, int) and seed > max_seed:
            max_seed = seed
    return ((max_seed // 100000) + 1) * 100000


def _build_id_mapping(base_elements: list, new_elements: list) -> dict:
    base_ids = {el["id"] for el in base_elements if "id" in el}
    used_ids = set(base_ids)
    mapping: dict[str, str] = {}
    for el in new_elements:
        old_id = el.get("id")
        if old_id is None:
            continue
        if old_id in base_ids:
            n = 2
            new_id = f"{old_id}_{n}"
            while new_id in used_ids:
                n += 1
                new_id = f"{old_id}_{n}"
            mapping[old_id] = new_id
            used_ids.add(new_id)
        else:
            used_ids.add(old_id)
    return mapping


def _remap_references(elements: list, mapping: dict) -> None:
    if not mapping:
        # still need to apply the id rename pass for elements themselves
        # (no-op when mapping is empty)
        return
    for el in elements:
        # Element's own id
        if "id" in el and el["id"] in mapping:
            el["id"] = mapping[el["id"]]
        # containerId
        cid = el.get("containerId")
        if isinstance(cid, str) and cid in mapping:
            el["containerId"] = mapping[cid]
        # boundElements: list of {id, type}
        bound = el.get("boundElements")
        if isinstance(bound, list):
            for ref in bound:
                if isinstance(ref, dict):
                    rid = ref.get("id")
                    if isinstance(rid, str) and rid in mapping:
                        ref["id"] = mapping[rid]
        # startBinding / endBinding
        for key in ("startBinding", "endBinding"):
            binding = el.get(key)
            if isinstance(binding, dict):
                eid = binding.get("elementId")
                if isinstance(eid, str) and eid in mapping:
                    binding["elementId"] = mapping[eid]


def _apply_seed_offset(elements: list, offset: int) -> tuple[int, int]:
    """Returns (min_new_seed, max_new_seed) over elements that have seeds."""
    min_seed: int | None = None
    max_seed: int | None = None
    for el in elements:
        seed = el.get("seed")
        if isinstance(seed, int):
            new_seed = seed + offset
            el["seed"] = new_seed
            if min_seed is None or new_seed < min_seed:
                min_seed = new_seed
            if max_seed is None or new_seed > max_seed:
                max_seed = new_seed
    return (min_seed or 0, max_seed or 0)


def _next_available_y(elements: list) -> float:
    if not elements:
        return 0
    bottoms = []
    for el in elements:
        y = el.get("y", 0)
        h = el.get("height", 0)
        try:
            bottoms.append(float(y) + float(h))
        except (TypeError, ValueError):
            continue
    if not bottoms:
        return 0
    return max(bottoms) + 60


def _atomic_write(path: Path, data) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    except OSError as exc:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass
        _die(f"could not write {path}: {exc}")


def _format_y(y: float) -> str:
    if float(y).is_integer():
        return str(int(y))
    return f"{y:g}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Merge a new section's element array into an existing "
            ".excalidraw file with automatic seed-namespacing and ID "
            "collision handling."
        )
    )
    parser.add_argument("base", type=Path, help="Path to base .excalidraw file")
    parser.add_argument(
        "section",
        type=Path,
        help="Path to JSON file containing an array of element objects",
    )
    args = parser.parse_args(argv)

    base_path: Path = args.base
    section_path: Path = args.section

    base_data = _load_json(base_path)
    section_data = _load_json(section_path)

    base_elements = _validate_base(base_data)
    new_elements_raw = _validate_section(section_data)

    # Deep copy via JSON round-trip so we don't mutate the original parsed
    # section data prior to the validation completing successfully. Validation
    # already happened, but we still want to operate on a fresh list.
    new_elements = json.loads(json.dumps(new_elements_raw))

    seed_offset = _compute_seed_offset(base_elements)
    mapping = _build_id_mapping(base_elements, new_elements)

    _remap_references(new_elements, mapping)
    min_new_seed, max_new_seed = _apply_seed_offset(new_elements, seed_offset)

    base_data["elements"] = base_elements + new_elements

    next_y = _next_available_y(base_data["elements"])

    _atomic_write(base_path, base_data)

    appended = len(new_elements)
    print(f"Merged {appended} elements into {base_path.name}")
    if appended > 0:
        if min_new_seed == 0 and max_new_seed == 0:
            print("  seed range: (no seeded elements)")
        elif min_new_seed == max_new_seed:
            print(f"  seed range: {min_new_seed}")
        else:
            print(f"  seed range: {min_new_seed}–{max_new_seed}")
    if mapping:
        renames = ", ".join(f"{old}→{new}" for old, new in mapping.items())
        print(f"  renamed IDs: {len(mapping)} ({renames})")
    else:
        print("  renamed IDs: 0")
    print(f"  next available y: {_format_y(next_y)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
