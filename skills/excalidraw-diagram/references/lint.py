#!/usr/bin/env python3
"""Static analyzer for .excalidraw JSON files.

Catches common authoring issues (overlapping elements, text overflow,
dangling arrows, over-use of containers, missing required fields) BEFORE
the slow render-validate loop.

Usage:
    python lint.py path/to/file.excalidraw

Exit code: 0 if no issues, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

# Background color used by the skill's "evidence artifact" pattern (dark rect
# holding code-snippet text).  Overlap between this rect and its children is
# intentional and should not be flagged.
EVIDENCE_BG = "#1e293b"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _bbox(el: dict[str, Any]) -> tuple[float, float, float, float] | None:
    """Return (x1, y1, x2, y2) for an element, or None if coords missing."""
    x = el.get("x")
    y = el.get("y")
    w = el.get("width", 0) or 0
    h = el.get("height", 0) or 0
    if x is None or y is None:
        return None
    return (float(x), float(y), float(x) + float(w), float(y) + float(h))


def _intersect_area(
    a: tuple[float, float, float, float],
    b: tuple[float, float, float, float],
) -> float:
    ix1 = max(a[0], b[0])
    iy1 = max(a[1], b[1])
    ix2 = min(a[2], b[2])
    iy2 = min(a[3], b[3])
    if ix2 <= ix1 or iy2 <= iy1:
        return 0.0
    return (ix2 - ix1) * (iy2 - iy1)


def _area(b: tuple[float, float, float, float]) -> float:
    return max(0.0, (b[2] - b[0]) * (b[3] - b[1]))


def _point_in_bbox(
    px: float, py: float, b: tuple[float, float, float, float]
) -> bool:
    return b[0] <= px <= b[2] and b[1] <= py <= b[3]


def _live(elements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [el for el in elements if not el.get("isDeleted", False)]


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_overlap(elements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flag pairs of free-floating elements whose bboxes overlap >20% of smaller."""
    warnings: list[dict[str, Any]] = []
    skip_types = {"line", "arrow", "freedraw"}
    live = [el for el in _live(elements) if el.get("type") not in skip_types]

    # Build binding sets so we don't flag legitimate parent/child or bound pairs.
    bound_pairs: set[tuple[str, str]] = set()
    for el in live:
        eid = el.get("id")
        cid = el.get("containerId")
        if eid and cid:
            bound_pairs.add(tuple(sorted([eid, cid])))  # type: ignore[arg-type]
        for be in el.get("boundElements") or []:
            bid = be.get("id") if isinstance(be, dict) else None
            if eid and bid:
                bound_pairs.add(tuple(sorted([eid, bid])))  # type: ignore[arg-type]

    for i in range(len(live)):
        a = live[i]
        ba = _bbox(a)
        if ba is None:
            continue
        area_a = _area(ba)
        if area_a <= 0:
            continue
        for j in range(i + 1, len(live)):
            b = live[j]
            bb = _bbox(b)
            if bb is None:
                continue
            area_b = _area(bb)
            if area_b <= 0:
                continue
            aid = a.get("id", "?")
            bid = b.get("id", "?")
            if tuple(sorted([aid, bid])) in bound_pairs:
                continue
            inter = _intersect_area(ba, bb)
            if inter <= 0:
                continue
            # Skip overlap when the larger element is an evidence-artifact rect.
            if area_a >= area_b:
                larger_el = a
            else:
                larger_el = b
            if larger_el.get("backgroundColor") == EVIDENCE_BG:
                continue
            smaller = min(area_a, area_b)
            ratio = inter / smaller if smaller > 0 else 0.0
            if ratio > 0.20:
                warnings.append(
                    {
                        "type": "overlap",
                        "msg": f"elements '{aid}' and '{bid}' overlap "
                        f"({int(round(ratio * 100))}% of smaller)",
                        "ids": [aid, bid],
                    }
                )
    return warnings


def check_text_overflow(elements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """For text-in-container, check if text plausibly fits."""
    warnings: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {
        el.get("id"): el for el in _live(elements) if el.get("id")
    }

    for el in _live(elements):
        if el.get("type") != "text":
            continue
        cid = el.get("containerId")
        if not cid:
            continue
        container = by_id.get(cid)
        if container is None:
            continue
        text = el.get("text", "") or ""
        font_size = el.get("fontSize", 16) or 16
        lines = text.split("\n") if text else [""]
        max_line_chars = max((len(line) for line in lines), default=0)
        n_lines = len(lines)

        est_w = max_line_chars * font_size * 0.55
        est_h = n_lines * font_size * 1.4

        c_w = container.get("width", 0) or 0
        c_h = container.get("height", 0) or 0
        eid = el.get("id", "?")

        if c_w and est_w > c_w:
            warnings.append(
                {
                    "type": "text-overflow",
                    "msg": f"text '{eid}' ({max_line_chars} chars x {int(font_size)}px) "
                    f"likely exceeds container '{cid}' (width {int(c_w)}, est. {int(est_w)})",
                    "ids": [eid, cid],
                }
            )
        if c_h and est_h > c_h:
            warnings.append(
                {
                    "type": "text-overflow",
                    "msg": f"text '{eid}' ({n_lines} lines x {int(font_size)}px) "
                    f"likely exceeds container '{cid}' (height {int(c_h)}, est. {int(est_h)})",
                    "ids": [eid, cid],
                }
            )
    return warnings


def check_dangling_arrows(elements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Arrows whose endpoints don't fall on any element AND lack a binding."""
    warnings: list[dict[str, Any]] = []
    live = _live(elements)
    bboxes: list[tuple[float, float, float, float]] = []
    for el in live:
        if el.get("type") in {"arrow", "line"}:
            continue
        bb = _bbox(el)
        if bb is not None:
            bboxes.append(bb)

    def _outside_all(px: float, py: float) -> bool:
        return not any(_point_in_bbox(px, py, b) for b in bboxes)

    for el in live:
        if el.get("type") != "arrow":
            continue
        x = el.get("x")
        y = el.get("y")
        points = el.get("points") or []
        if x is None or y is None or not points:
            continue
        try:
            sx, sy = float(x), float(y)
            last = points[-1]
            ex = sx + float(last[0])
            ey = sy + float(last[1])
        except (TypeError, ValueError, IndexError):
            continue

        start_binding = el.get("startBinding")
        end_binding = el.get("endBinding")
        eid = el.get("id", "?")

        if start_binding is None and _outside_all(sx, sy):
            warnings.append(
                {
                    "type": "dangling-arrow",
                    "msg": f"arrow '{eid}' start point ({int(sx)}, {int(sy)}) "
                    f"outside any element",
                    "ids": [eid],
                }
            )
        if end_binding is None and _outside_all(ex, ey):
            warnings.append(
                {
                    "type": "dangling-arrow",
                    "msg": f"arrow '{eid}' end point ({int(ex)}, {int(ey)}) "
                    f"outside any element",
                    "ids": [eid],
                }
            )
    return warnings


def check_container_ratio(
    elements: list[dict[str, Any]], max_ratio: float = 0.30
) -> list[dict[str, Any]]:
    """Single warning if too many text elements live inside containers."""
    texts = [el for el in _live(elements) if el.get("type") == "text"]
    total = len(texts)
    if total == 0:
        return []
    in_container = sum(1 for el in texts if el.get("containerId"))
    ratio = in_container / total
    if ratio > max_ratio:
        return [
            {
                "type": "container-ratio",
                "msg": f"{in_container}/{total} text elements in containers "
                f"({int(round(ratio * 100))}% > {int(round(max_ratio * 100))}%)",
                "ids": [el.get("id", "?") for el in texts if el.get("containerId")],
            }
        ]
    return []


def check_missing_required_fields(
    elements: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Every element needs type, x, y, id."""
    warnings: list[dict[str, Any]] = []
    required = ("type", "x", "y", "id")
    for idx, el in enumerate(_live(elements)):
        missing = [f for f in required if f not in el or el.get(f) is None]
        if missing:
            eid = el.get("id", f"<index {idx}>")
            warnings.append(
                {
                    "type": "missing-required",
                    "msg": f"element '{eid}' missing required field(s): "
                    f"{', '.join(missing)}",
                    "ids": [el.get("id")] if el.get("id") else [],
                }
            )
    return warnings


def check_text_centering(elements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Text inside a shape MUST be centered both axes via the containerId pattern.

    Catches three failure modes:
      1. Text has containerId but textAlign != "center" or verticalAlign != "middle"
         → renders top/left-aligned, looks broken.
      2. Text is geometrically inside a non-evidence shape but has no containerId
         → free-floating text glued to top of shape (the regression we hit).
      3. Container's boundElements does not list back the bound text
         → reverse link missing, Excalidraw can't center.

    Evidence artifacts (backgroundColor == EVIDENCE_BG) are exempt — code
    blocks intentionally use top-left alignment.
    """
    warnings: list[dict[str, Any]] = []
    by_id = {el.get("id"): el for el in _live(elements) if el.get("id")}

    # Failure mode 1 + 3: explicit containerId set but alignment wrong / reverse link missing
    for el in _live(elements):
        if el.get("type") != "text":
            continue
        cid = el.get("containerId")
        if not cid:
            continue
        if el.get("textAlign") != "center" or el.get("verticalAlign") != "middle":
            warnings.append(
                {
                    "type": "text-not-centered",
                    "msg": (
                        f"text '{el.get('id')}' has containerId='{cid}' but "
                        f"textAlign={el.get('textAlign')!r} verticalAlign="
                        f"{el.get('verticalAlign')!r} (must be 'center' / 'middle')"
                    ),
                    "ids": [el.get("id"), cid],
                }
            )
        container = by_id.get(cid)
        if container is not None:
            bound = container.get("boundElements") or []
            if not any(
                isinstance(b, dict) and b.get("id") == el.get("id") for b in bound
            ):
                warnings.append(
                    {
                        "type": "text-binding-broken",
                        "msg": (
                            f"text '{el.get('id')}' references container '{cid}' "
                            f"but container's boundElements does not include it back"
                        ),
                        "ids": [el.get("id"), cid],
                    }
                )

    # Failure mode 4: bound text bbox >> actual text height → glyphs glue to top
    # Excalidraw 0.18.x doesn't honor verticalAlign:middle when bbox is much
    # taller than the rendered text. Recompute expected height; flag if delta > 2x.
    for el in _live(elements):
        if el.get("type") != "text" or not el.get("containerId"):
            continue
        text_str = el.get("text", "") or ""
        font_size = el.get("fontSize", 16) or 16
        n_lines = max(text_str.count("\n") + 1, 1)
        # Expected single-line text height with default lineHeight ~1.25-1.4
        expected_h = n_lines * font_size * 1.4
        actual_h = el.get("height", 0) or 0
        if actual_h > expected_h * 2 and actual_h - expected_h > 20:
            warnings.append(
                {
                    "type": "text-bbox-too-tall",
                    "msg": (
                        f"text '{el.get('id')}' has height={actual_h:.0f}px but "
                        f"content needs ~{expected_h:.0f}px. Excalidraw will glue "
                        f"glyphs to TOP — set text.height to estimate_text_size() "
                        f"and offset y to center inside container."
                    ),
                    "ids": [el.get("id"), el.get("containerId")],
                }
            )

    # Failure mode 2: text geometrically inside non-evidence shape without containerId
    shapes = [
        el for el in _live(elements)
        if el.get("type") in ("rectangle", "ellipse", "diamond")
        and el.get("backgroundColor") != EVIDENCE_BG
    ]
    for txt in _live(elements):
        if txt.get("type") != "text" or txt.get("containerId"):
            continue
        tb = _bbox(txt)
        if tb is None:
            continue
        tx1, ty1, tx2, ty2 = tb
        # Use centroid to decide "inside"
        cx, cy = (tx1 + tx2) / 2, (ty1 + ty2) / 2
        for shape in shapes:
            sb = _bbox(shape)
            if sb is None:
                continue
            sx1, sy1, sx2, sy2 = sb
            if sx1 <= cx <= sx2 and sy1 <= cy <= sy2:
                # Skip tiny shapes (markers/dots) — they don't host text
                if (sx2 - sx1) < 30 or (sy2 - sy1) < 30:
                    continue
                warnings.append(
                    {
                        "type": "text-floating-in-shape",
                        "msg": (
                            f"text '{txt.get('id')}' sits inside shape "
                            f"'{shape.get('id')}' but has no containerId — "
                            f"will not be centered. Bind via containerId or "
                            f"move text outside the shape."
                        ),
                        "ids": [txt.get("id"), shape.get("id")],
                    }
                )
                break

    return warnings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


CHECKS = [
    check_missing_required_fields,
    check_overlap,
    check_text_overflow,
    check_dangling_arrows,
    check_text_centering,
]


def lint_file(path: str, *, container_ratio_max: float = 0.30) -> int:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"{path}: file not found", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"{path}: invalid JSON ({e})", file=sys.stderr)
        return 1

    elements = data.get("elements") if isinstance(data, dict) else None
    if not isinstance(elements, list):
        print(f"{path}: no 'elements' array found", file=sys.stderr)
        return 1

    all_warnings: list[dict[str, Any]] = []
    for check in CHECKS:
        try:
            all_warnings.extend(check(elements))
        except Exception as e:  # noqa: BLE001 - keep linter robust
            all_warnings.append(
                {
                    "type": "lint-internal-error",
                    "msg": f"check {check.__name__} raised {type(e).__name__}: {e}",
                    "ids": [],
                }
            )

    # Container-ratio check uses a configurable threshold.
    try:
        all_warnings.extend(
            check_container_ratio(elements, max_ratio=container_ratio_max)
        )
    except Exception as e:  # noqa: BLE001
        all_warnings.append(
            {
                "type": "lint-internal-error",
                "msg": f"check check_container_ratio raised {type(e).__name__}: {e}",
                "ids": [],
            }
        )

    name = path.rsplit("/", 1)[-1]
    print(f"{name} - {len(all_warnings)} issues")
    for w in all_warnings:
        print(f"  [{w['type']}] {w['msg']}")

    return 0 if not all_warnings else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Lint an .excalidraw JSON file for common authoring issues."
    )
    parser.add_argument("path", help="Path to .excalidraw file")
    parser.add_argument(
        "--container-ratio-max",
        type=float,
        default=0.30,
        help="Maximum allowed ratio of text elements inside containers (default: 0.30)",
    )
    args = parser.parse_args(argv)
    return lint_file(args.path, container_ratio_max=args.container_ratio_max)


if __name__ == "__main__":
    sys.exit(main())
