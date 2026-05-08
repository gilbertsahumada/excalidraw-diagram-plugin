"""Chart-element generators for Excalidraw diagrams.

Pure-Python helpers that emit Excalidraw element dicts for common chart
patterns (bar chart, line chart, pie-as-stacked-bar). Output is a list of
element dicts ready to append to an `elements` array in a `.excalidraw`
JSON file.

Conventions matching the rest of the skill:
- roughness: 0
- fontFamily: 3 (Cascadia Code monospace)
- opacity: 100
- Palette colors (defaults match references/color-palette.md):
    primary fill   #3b82f6 / stroke #1e3a5f
    title text     #1e40af
    body/detail    #64748b
- No external dependencies beyond stdlib (math).
- Element IDs are namespaced as `chart_<seed_base>_<role>_<index>` so
  multiple chart calls in one diagram do not collide as long as you
  pass distinct seed_base values.

Excalidraw convention: x grows right, y grows downward.
"""

from __future__ import annotations

import math
from typing import Any


# ---------------------------------------------------------------------------
# Palette defaults (match color-palette.md)
# ---------------------------------------------------------------------------

PRIMARY_FILL = "#3b82f6"
PRIMARY_STROKE = "#1e3a5f"
TITLE_COLOR = "#1e40af"
SUBTITLE_COLOR = "#3b82f6"
DETAIL_COLOR = "#64748b"
AXIS_COLOR = "#1e3a5f"
DOT_COLOR = "#3b82f6"

# Dark-mode equivalents (inverted: dark fill + bright stroke).
# Use when appState.viewBackgroundColor is dark (#0f172a).
DARK_BACKGROUND = "#0f172a"
DARK_PRIMARY_FILL = "#1e3a8a"
DARK_PRIMARY_STROKE = "#60a5fa"
DARK_TITLE_COLOR = "#f1f5f9"
DARK_SUBTITLE_COLOR = "#cbd5e1"
DARK_DETAIL_COLOR = "#94a3b8"
DARK_AXIS_COLOR = "#94a3b8"
DARK_DOT_COLOR = "#60a5fa"
DARK_EVIDENCE_BG = "#020617"
DARK_EVIDENCE_TEXT = "#4ade80"


THEMES = {
    "light": {
        "bg": "#ffffff",
        "primary_fill": PRIMARY_FILL,
        "primary_stroke": PRIMARY_STROKE,
        "title": TITLE_COLOR,
        "subtitle": SUBTITLE_COLOR,
        "detail": DETAIL_COLOR,
        "axis": AXIS_COLOR,
        "dot": DOT_COLOR,
        "evidence_bg": "#1e293b",
        "evidence_text": "#22c55e",
    },
    "dark": {
        "bg": DARK_BACKGROUND,
        "primary_fill": DARK_PRIMARY_FILL,
        "primary_stroke": DARK_PRIMARY_STROKE,
        "title": DARK_TITLE_COLOR,
        "subtitle": DARK_SUBTITLE_COLOR,
        "detail": DARK_DETAIL_COLOR,
        "axis": DARK_AXIS_COLOR,
        "dot": DARK_DOT_COLOR,
        "evidence_bg": DARK_EVIDENCE_BG,
        "evidence_text": DARK_EVIDENCE_TEXT,
    },
}


def theme(name: str = "light") -> dict:
    """Return theme color dict. Pass 'dark' for dark canvas, 'light' for white.

    Use:
        t = theme('dark')
        rect_fill = t['primary_fill']
        title_color = t['title']
        bg = t['bg']  # set on appState.viewBackgroundColor
    """
    return THEMES.get(name, THEMES["light"])


# ---------------------------------------------------------------------------
# Element factories
# ---------------------------------------------------------------------------


def _base(seed: int, version_nonce: int | None = None) -> dict[str, Any]:
    """Return the common required-field dict every Excalidraw element needs."""
    return {
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 0,
        "opacity": 100,
        "angle": 0,
        "seed": seed,
        "version": 1,
        "versionNonce": version_nonce if version_nonce is not None else seed + 1,
        "isDeleted": False,
        "groupIds": [],
        "boundElements": None,
        "link": None,
        "locked": False,
    }


def _rect(
    elem_id: str,
    x: int,
    y: int,
    width: int,
    height: int,
    seed: int,
    fill: str,
    stroke: str,
    stroke_width: int = 2,
    rounded: bool = True,
) -> dict[str, Any]:
    el = _base(seed)
    el.update(
        {
            "type": "rectangle",
            "id": elem_id,
            "x": int(x),
            "y": int(y),
            "width": int(width),
            "height": int(height),
            "strokeColor": stroke,
            "backgroundColor": fill,
            "strokeWidth": stroke_width,
            "roundness": {"type": 3} if rounded else None,
        }
    )
    return el


def _line(
    elem_id: str,
    x: int,
    y: int,
    points: list[list[int]],
    seed: int,
    stroke: str,
    stroke_width: int = 2,
    stroke_style: str = "solid",
) -> dict[str, Any]:
    # Compute width/height from points (relative to x,y).
    xs = [p[0] for p in points] or [0]
    ys = [p[1] for p in points] or [0]
    width = max(xs) - min(xs)
    height = max(ys) - min(ys)
    el = _base(seed)
    el.update(
        {
            "type": "line",
            "id": elem_id,
            "x": int(x),
            "y": int(y),
            "width": int(width),
            "height": int(height),
            "strokeColor": stroke,
            "backgroundColor": "transparent",
            "strokeWidth": stroke_width,
            "strokeStyle": stroke_style,
            "points": [[int(p[0]), int(p[1])] for p in points],
        }
    )
    return el


def _text(
    elem_id: str,
    x: int,
    y: int,
    width: int,
    height: int,
    text: str,
    seed: int,
    color: str = DETAIL_COLOR,
    font_size: int = 14,
    text_align: str = "left",
    vertical_align: str = "top",
) -> dict[str, Any]:
    el = _base(seed)
    el.update(
        {
            "type": "text",
            "id": elem_id,
            "x": int(x),
            "y": int(y),
            "width": int(width),
            "height": int(height),
            "text": text,
            "originalText": text,
            "fontSize": font_size,
            "fontFamily": 3,
            "textAlign": text_align,
            "verticalAlign": vertical_align,
            "strokeColor": color,
            "backgroundColor": "transparent",
            "containerId": None,
            "lineHeight": 1.25,
        }
    )
    return el


def _ellipse(
    elem_id: str,
    cx: int,
    cy: int,
    radius: int,
    seed: int,
    fill: str = DOT_COLOR,
    stroke: str = DOT_COLOR,
) -> dict[str, Any]:
    diameter = max(2, radius * 2)
    el = _base(seed)
    el.update(
        {
            "type": "ellipse",
            "id": elem_id,
            "x": int(cx - radius),
            "y": int(cy - radius),
            "width": diameter,
            "height": diameter,
            "strokeColor": stroke,
            "backgroundColor": fill,
            "strokeWidth": 1,
        }
    )
    return el


# ---------------------------------------------------------------------------
# Helpers for nice axis ticks
# ---------------------------------------------------------------------------


def _format_value(v: float) -> str:
    if v == int(v):
        return f"{int(v)}"
    if abs(v) < 10:
        return f"{v:.2f}".rstrip("0").rstrip(".")
    return f"{v:.1f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def bar_chart(
    x: int,
    y: int,
    width: int,
    height: int,
    data: list[tuple[str, float]],
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    seed_base: int = 700000,
    color: str = PRIMARY_FILL,
    stroke: str = PRIMARY_STROKE,
) -> list[dict[str, Any]]:
    """Generate Excalidraw elements for a bar chart inside the bbox at (x, y).

    Bars are rectangles whose heights are proportional to the largest value in
    `data`. Includes y-axis tick labels at 0 and max, x-axis category labels
    under each bar, optional title, and optional axis labels.

    Layout inside the (x, y, width, height) bbox:
      - top reserve for title (~30 px)
      - left reserve for y_label and tick labels (~70 px)
      - bottom reserve for x category labels and x_label (~50 px)
      - the rest is the plot area

    Returns a list of element dicts (rectangles, lines, texts).
    """
    elements: list[dict[str, Any]] = []
    if not data:
        return elements

    # --- layout reserves
    title_h = 30 if title else 0
    y_label_w = 24 if y_label else 0
    tick_w = 46
    plot_left = x + y_label_w + tick_w
    plot_top = y + title_h + 10
    x_label_h = 22 if x_label else 0
    cat_label_h = 24
    plot_bottom = y + height - cat_label_h - x_label_h
    plot_right = x + width - 10

    plot_w = max(10, plot_right - plot_left)
    plot_h = max(10, plot_bottom - plot_top)

    max_val = max((v for _, v in data), default=1.0)
    if max_val <= 0:
        max_val = 1.0

    n = len(data)
    gap = max(8, plot_w // (n * 6))
    bar_w = max(8, (plot_w - gap * (n + 1)) // n)

    # --- title
    if title:
        elements.append(
            _text(
                f"chart_{seed_base}_title_0",
                x,
                y,
                width,
                title_h,
                title,
                seed=seed_base + 1,
                color=TITLE_COLOR,
                font_size=20,
                text_align="left",
                vertical_align="top",
            )
        )

    # --- y axis line
    elements.append(
        _line(
            f"chart_{seed_base}_yaxis_0",
            plot_left,
            plot_top,
            [[0, 0], [0, plot_h]],
            seed=seed_base + 10,
            stroke=AXIS_COLOR,
            stroke_width=2,
        )
    )
    # --- x axis line
    elements.append(
        _line(
            f"chart_{seed_base}_xaxis_0",
            plot_left,
            plot_bottom,
            [[0, 0], [plot_w, 0]],
            seed=seed_base + 11,
            stroke=AXIS_COLOR,
            stroke_width=2,
        )
    )

    # --- y tick labels at 0 and max
    elements.append(
        _text(
            f"chart_{seed_base}_ytick_0",
            plot_left - tick_w - 2,
            plot_bottom - 8,
            tick_w,
            16,
            _format_value(0),
            seed=seed_base + 20,
            color=DETAIL_COLOR,
            font_size=12,
            text_align="right",
            vertical_align="top",
        )
    )
    elements.append(
        _text(
            f"chart_{seed_base}_ytick_1",
            plot_left - tick_w - 2,
            plot_top - 6,
            tick_w,
            16,
            _format_value(max_val),
            seed=seed_base + 21,
            color=DETAIL_COLOR,
            font_size=12,
            text_align="right",
            vertical_align="top",
        )
    )

    # --- y axis label (rotated visually impractical; place above tick stack)
    if y_label:
        elements.append(
            _text(
                f"chart_{seed_base}_ylabel_0",
                x,
                plot_top - 22,
                y_label_w + tick_w,
                18,
                y_label,
                seed=seed_base + 30,
                color=SUBTITLE_COLOR,
                font_size=12,
                text_align="left",
                vertical_align="top",
            )
        )

    # --- bars + category labels
    cursor_x = plot_left + gap
    for i, (label, value) in enumerate(data):
        ratio = max(0.0, min(1.0, value / max_val))
        bar_h = max(2, int(round(plot_h * ratio)))
        bar_x = cursor_x
        bar_y = plot_bottom - bar_h
        elements.append(
            _rect(
                f"chart_{seed_base}_bar_{i}",
                bar_x,
                bar_y,
                bar_w,
                bar_h,
                seed=seed_base + 100 + i,
                fill=color,
                stroke=stroke,
                stroke_width=2,
            )
        )
        # value label above bar
        elements.append(
            _text(
                f"chart_{seed_base}_value_{i}",
                bar_x - 4,
                bar_y - 18,
                bar_w + 8,
                16,
                _format_value(value),
                seed=seed_base + 200 + i,
                color=TITLE_COLOR,
                font_size=12,
                text_align="center",
                vertical_align="top",
            )
        )
        # category label below x-axis
        elements.append(
            _text(
                f"chart_{seed_base}_catlabel_{i}",
                bar_x - 6,
                plot_bottom + 4,
                bar_w + 12,
                18,
                label,
                seed=seed_base + 300 + i,
                color=DETAIL_COLOR,
                font_size=12,
                text_align="center",
                vertical_align="top",
            )
        )
        cursor_x += bar_w + gap

    # --- x label (under category labels)
    if x_label:
        elements.append(
            _text(
                f"chart_{seed_base}_xlabel_0",
                plot_left,
                plot_bottom + cat_label_h + 2,
                plot_w,
                x_label_h,
                x_label,
                seed=seed_base + 40,
                color=SUBTITLE_COLOR,
                font_size=12,
                text_align="center",
                vertical_align="top",
            )
        )

    return elements


def grouped_bar_chart(
    x: int,
    y: int,
    width: int,
    height: int,
    data: dict[str, list[tuple[str, float]]],
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    seed_base: int = 750000,
    colors: list[str] | None = None,
    strokes: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Multi-series bar chart with grouped bars per category.

    data: {"Series A": [("cat1", 10), ("cat2", 20)], "Series B": [("cat1", 15), ("cat2", 25)]}
    All series must share the same category names in the same order.
    colors: one fill color per series. Defaults to palette cycle.
    """
    elements: list[dict[str, Any]] = []
    if not data:
        return elements

    series_names = list(data.keys())
    n_series = len(series_names)
    categories = [cat for cat, _ in data[series_names[0]]]
    n_cats = len(categories)

    if n_cats == 0:
        return elements

    # Defaults
    if colors is None:
        colors = ["#3b82f6", "#60a5fa", "#a7f3d0", "#fed7aa", "#ddd6fe"][:n_series]
    if strokes is None:
        strokes = ["#1e3a5f", "#1e3a5f", "#047857", "#c2410c", "#6d28d9"][:n_series]

    # Compute max value across all series
    max_val = max(v for series_data in data.values() for _, v in series_data)
    if max_val <= 0:
        max_val = 1.0

    # Layout reserves
    title_h = 30 if title else 0
    y_label_w = 24 if y_label else 0
    tick_w = 46
    plot_left = x + y_label_w + tick_w
    plot_top = y + title_h + 10
    x_label_h = 22 if x_label else 0
    cat_label_h = 24
    plot_bottom = y + height - cat_label_h - x_label_h
    plot_right = x + width - 10

    plot_w = max(10, plot_right - plot_left)
    plot_h = max(10, plot_bottom - plot_top)

    # Group/bar dimensions
    group_width = (plot_w - 60) / n_cats  # 60 for y-axis margin
    bar_width = (group_width - 10) / n_series  # 10 padding between groups

    seed = seed_base

    # Title
    if title:
        seed += 1
        elements.append(
            _text(
                f"chart_{seed_base}_title_0",
                x,
                y,
                width,
                title_h,
                title,
                seed=seed,
                color=TITLE_COLOR,
                font_size=20,
                text_align="left",
                vertical_align="top",
            )
        )

    # Y-axis line
    seed += 1
    elements.append(
        _line(
            f"chart_{seed_base}_yaxis_0",
            plot_left,
            plot_top,
            [[0, 0], [0, plot_h]],
            seed=seed,
            stroke=AXIS_COLOR,
            stroke_width=2,
        )
    )

    # X-axis line
    seed += 1
    elements.append(
        _line(
            f"chart_{seed_base}_xaxis_0",
            plot_left,
            plot_bottom,
            [[0, 0], [plot_w, 0]],
            seed=seed,
            stroke=AXIS_COLOR,
            stroke_width=2,
        )
    )

    # Y tick labels (0 and max_val)
    seed += 1
    elements.append(
        _text(
            f"chart_{seed_base}_ytick_0",
            plot_left - tick_w - 2,
            plot_bottom - 8,
            tick_w,
            16,
            _format_value(0),
            seed=seed,
            color=DETAIL_COLOR,
            font_size=12,
            text_align="right",
            vertical_align="top",
        )
    )
    seed += 1
    elements.append(
        _text(
            f"chart_{seed_base}_ytick_1",
            plot_left - tick_w - 2,
            plot_top - 6,
            tick_w,
            16,
            _format_value(max_val),
            seed=seed,
            color=DETAIL_COLOR,
            font_size=12,
            text_align="right",
            vertical_align="top",
        )
    )

    # Y-axis label
    if y_label:
        seed += 1
        elements.append(
            _text(
                f"chart_{seed_base}_ylabel_0",
                x,
                plot_top - 22,
                y_label_w + tick_w,
                18,
                y_label,
                seed=seed,
                color=SUBTITLE_COLOR,
                font_size=12,
                text_align="left",
                vertical_align="top",
            )
        )

    # Bars per category
    group_start_x = plot_left + 30  # offset from y-axis
    for cat_i, cat_name in enumerate(categories):
        group_x = group_start_x + cat_i * group_width
        for s_i, series_name in enumerate(series_names):
            value = data[series_name][cat_i][1]
            ratio = max(0.0, min(1.0, value / max_val))
            bar_h = max(2, int(round(plot_h * ratio)))
            bar_x = group_x + s_i * bar_width
            bar_y = plot_bottom - bar_h

            seed += 1
            elements.append(
                _rect(
                    f"chart_{seed_base}_bar_{cat_i}_{s_i}",
                    bar_x,
                    bar_y,
                    int(bar_width),
                    bar_h,
                    seed=seed,
                    fill=colors[s_i % len(colors)],
                    stroke=strokes[s_i % len(strokes)],
                    stroke_width=2,
                )
            )

            # Value label above bar
            seed += 1
            elements.append(
                _text(
                    f"chart_{seed_base}_value_{cat_i}_{s_i}",
                    int(bar_x),
                    bar_y - 18,
                    int(bar_width),
                    16,
                    _format_value(value),
                    seed=seed,
                    color=TITLE_COLOR,
                    font_size=12,
                    text_align="center",
                    vertical_align="top",
                )
            )

        # Category label below group
        seed += 1
        elements.append(
            _text(
                f"chart_{seed_base}_catlabel_{cat_i}",
                int(group_x),
                plot_bottom + 4,
                int(group_width),
                18,
                cat_name,
                seed=seed,
                color=DETAIL_COLOR,
                font_size=12,
                text_align="center",
                vertical_align="top",
            )
        )

    # X-label
    if x_label:
        seed += 1
        elements.append(
            _text(
                f"chart_{seed_base}_xlabel_0",
                plot_left,
                plot_bottom + cat_label_h + 2,
                plot_w,
                x_label_h,
                x_label,
                seed=seed,
                color=SUBTITLE_COLOR,
                font_size=12,
                text_align="center",
                vertical_align="top",
            )
        )

    # Legend (top-right corner)
    legend_x = x + width - 140
    legend_y_start = y + title_h + 10
    for s_i, series_name in enumerate(series_names):
        rect_y = legend_y_start + s_i * 20
        seed += 1
        elements.append(
            _rect(
                f"chart_{seed_base}_legend_rect_{s_i}",
                legend_x,
                rect_y,
                12,
                12,
                seed=seed,
                fill=colors[s_i % len(colors)],
                stroke=strokes[s_i % len(strokes)],
                stroke_width=1,
            )
        )
        seed += 1
        elements.append(
            _text(
                f"chart_{seed_base}_legend_text_{s_i}",
                legend_x + 18,
                rect_y - 2,
                100,
                16,
                series_name,
                seed=seed,
                color=DETAIL_COLOR,
                font_size=12,
                text_align="left",
                vertical_align="top",
            )
        )

    return elements


def line_chart(
    x: int,
    y: int,
    width: int,
    height: int,
    data: list[tuple[str, float]],
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    seed_base: int = 800000,
    color: str = PRIMARY_FILL,
) -> list[dict[str, Any]]:
    """Generate Excalidraw elements for a simple line chart.

    Emits: title text, x/y axis lines, y-tick labels at 0 and max, a
    poly-line through the data points, small dot markers at each point,
    a value label per point, and category labels under the x axis.
    """
    elements: list[dict[str, Any]] = []
    if not data:
        return elements

    title_h = 30 if title else 0
    y_label_w = 24 if y_label else 0
    tick_w = 46
    plot_left = x + y_label_w + tick_w
    plot_top = y + title_h + 10
    x_label_h = 22 if x_label else 0
    cat_label_h = 24
    plot_bottom = y + height - cat_label_h - x_label_h
    plot_right = x + width - 10

    plot_w = max(10, plot_right - plot_left)
    plot_h = max(10, plot_bottom - plot_top)

    values = [v for _, v in data]
    max_val = max(values) if values else 1.0
    min_val = min(values) if values else 0.0
    span = max_val - min_val
    if span <= 0:
        span = max(abs(max_val), 1.0)

    n = len(data)
    if n == 1:
        xs = [plot_left + plot_w // 2]
    else:
        step = plot_w / (n - 1)
        xs = [int(round(plot_left + step * i)) for i in range(n)]

    def _y_for(v: float) -> int:
        ratio = (v - min_val) / span
        return int(round(plot_bottom - ratio * plot_h))

    pts_abs = [(xs[i], _y_for(values[i])) for i in range(n)]

    # title
    if title:
        elements.append(
            _text(
                f"chart_{seed_base}_title_0",
                x,
                y,
                width,
                title_h,
                title,
                seed=seed_base + 1,
                color=TITLE_COLOR,
                font_size=20,
            )
        )

    # axes
    elements.append(
        _line(
            f"chart_{seed_base}_yaxis_0",
            plot_left,
            plot_top,
            [[0, 0], [0, plot_h]],
            seed=seed_base + 10,
            stroke=AXIS_COLOR,
            stroke_width=2,
        )
    )
    elements.append(
        _line(
            f"chart_{seed_base}_xaxis_0",
            plot_left,
            plot_bottom,
            [[0, 0], [plot_w, 0]],
            seed=seed_base + 11,
            stroke=AXIS_COLOR,
            stroke_width=2,
        )
    )

    # y tick labels (min and max)
    elements.append(
        _text(
            f"chart_{seed_base}_ytick_0",
            plot_left - tick_w - 2,
            plot_bottom - 8,
            tick_w,
            16,
            _format_value(min_val),
            seed=seed_base + 20,
            color=DETAIL_COLOR,
            font_size=12,
            text_align="right",
        )
    )
    elements.append(
        _text(
            f"chart_{seed_base}_ytick_1",
            plot_left - tick_w - 2,
            plot_top - 6,
            tick_w,
            16,
            _format_value(max_val),
            seed=seed_base + 21,
            color=DETAIL_COLOR,
            font_size=12,
            text_align="right",
        )
    )

    if y_label:
        elements.append(
            _text(
                f"chart_{seed_base}_ylabel_0",
                x,
                plot_top - 22,
                y_label_w + tick_w,
                18,
                y_label,
                seed=seed_base + 30,
                color=SUBTITLE_COLOR,
                font_size=12,
            )
        )

    # the poly-line through points (relative coords)
    base_x = pts_abs[0][0]
    base_y = pts_abs[0][1]
    rel_pts = [[p[0] - base_x, p[1] - base_y] for p in pts_abs]
    elements.append(
        _line(
            f"chart_{seed_base}_polyline_0",
            base_x,
            base_y,
            rel_pts,
            seed=seed_base + 50,
            stroke=color,
            stroke_width=2,
        )
    )

    # dot markers + value/category labels
    for i, (label, value) in enumerate(data):
        cx, cy = pts_abs[i]
        elements.append(
            _ellipse(
                f"chart_{seed_base}_dot_{i}",
                cx,
                cy,
                radius=5,
                seed=seed_base + 100 + i,
                fill=color,
                stroke=color,
            )
        )
        elements.append(
            _text(
                f"chart_{seed_base}_value_{i}",
                cx - 24,
                cy - 22,
                48,
                16,
                _format_value(value),
                seed=seed_base + 200 + i,
                color=TITLE_COLOR,
                font_size=12,
                text_align="center",
            )
        )
        elements.append(
            _text(
                f"chart_{seed_base}_catlabel_{i}",
                cx - 30,
                plot_bottom + 4,
                60,
                18,
                label,
                seed=seed_base + 300 + i,
                color=DETAIL_COLOR,
                font_size=12,
                text_align="center",
            )
        )

    if x_label:
        elements.append(
            _text(
                f"chart_{seed_base}_xlabel_0",
                plot_left,
                plot_bottom + cat_label_h + 2,
                plot_w,
                x_label_h,
                x_label,
                seed=seed_base + 40,
                color=SUBTITLE_COLOR,
                font_size=12,
                text_align="center",
            )
        )

    return elements


def pie_slice_approximation(
    cx: int,
    cy: int,
    radius: int,
    data: list[tuple[str, float]],
    seed_base: int = 900000,
) -> list[dict[str, Any]]:
    """Approximate a pie chart as a horizontal stacked bar.

    Excalidraw has no native arc/wedge primitive; emitting many thin
    rectangles fanned around a center looks noisy and aliases at small
    sizes. Instead this function emits a horizontal stacked bar of width
    `2 * radius` centered at (cx, cy), with one rectangle per category
    sized proportionally to its share of the total. A legend with each
    category's percentage sits below the bar.

    Returns a list of element dicts (rectangles + texts).
    """
    elements: list[dict[str, Any]] = []
    if not data:
        return elements

    total = sum(max(0.0, v) for _, v in data)
    if total <= 0:
        return elements

    bar_w = max(40, radius * 2)
    bar_h = max(20, radius // 3)
    bar_x = int(cx - bar_w // 2)
    bar_y = int(cy - bar_h // 2)

    # palette of fills cycled across slices, all from approved palette
    fills = [
        ("#3b82f6", "#1e3a5f"),  # primary
        ("#60a5fa", "#1e3a5f"),  # secondary
        ("#93c5fd", "#1e3a5f"),  # tertiary
        ("#fed7aa", "#c2410c"),  # start/trigger
        ("#a7f3d0", "#047857"),  # end/success
        ("#ddd6fe", "#6d28d9"),  # ai/llm
        ("#fef3c7", "#b45309"),  # decision
        ("#dbeafe", "#1e40af"),  # inactive
    ]

    cursor_x = bar_x
    legend_y = bar_y + bar_h + 12
    for i, (label, value) in enumerate(data):
        share = max(0.0, value) / total
        seg_w = int(round(bar_w * share))
        if i == len(data) - 1:
            # Force last segment to fill the remainder so widths sum exactly.
            seg_w = bar_x + bar_w - cursor_x
        fill, stroke = fills[i % len(fills)]
        elements.append(
            _rect(
                f"chart_{seed_base}_slice_{i}",
                cursor_x,
                bar_y,
                max(1, seg_w),
                bar_h,
                seed=seed_base + 100 + i,
                fill=fill,
                stroke=stroke,
                stroke_width=2,
            )
        )
        # legend text under segment
        pct = int(round(share * 100))
        elements.append(
            _text(
                f"chart_{seed_base}_legend_{i}",
                cursor_x,
                legend_y + (i * 16),
                max(80, bar_w),
                16,
                f"{label} - {pct}%",
                seed=seed_base + 200 + i,
                color=DETAIL_COLOR,
                font_size=12,
                text_align="left",
            )
        )
        cursor_x += seg_w

    return elements


def add_annotation(
    elements: list[dict],
    text: str,
    x: int,
    y: int,
    font_size: int = 13,
    color: str = "#64748b",
    seed_base: int = 790000,
) -> list[dict]:
    """Append a free-floating annotation text element to an existing elements list.
    Returns the extended list (mutates in place and returns for chaining)."""
    seed = seed_base + 1
    el = _text(
        f"chart_{seed_base}_annotation_0",
        x,
        y,
        len(text) * (font_size // 2 + 1),
        font_size + 4,
        text,
        seed=seed,
        color=color,
        font_size=font_size,
        text_align="left",
        vertical_align="top",
    )
    elements.append(el)
    return elements


def card_grid(
    x: int,
    y: int,
    cards: list[dict],
    cols: int = 3,
    card_width: int = 300,
    card_height: int = 200,
    gap_x: int = 30,
    gap_y: int = 30,
    seed_base: int = 860000,
    default_header_fill: str = PRIMARY_FILL,
    default_header_stroke: str = PRIMARY_STROKE,
    header_height: int = 45,
    stroke_style: str = "solid",
) -> list[dict[str, Any]]:
    """Generate a grid of styled cards as Excalidraw elements.

    Each card is a dict:
        {"title": str, "body": str, "fill": str (optional), "stroke": str (optional)}
    Cards are laid out in rows of `cols` columns. Each card has a colored header
    strip with the title and a light body area with text content.

    Example:
        card_grid(80, 200, [
            {"title": "Feature A", "body": "Does X and Y"},
            {"title": "Feature B", "body": "Does Z", "fill": "#c2410c", "stroke": "#7c2d12"},
            {"title": "Feature C", "body": "Does W"},
        ], cols=3, card_width=300, card_height=180)
    """
    elements: list[dict[str, Any]] = []
    seed = seed_base

    for i, card in enumerate(cards):
        col = i % cols
        row = i // cols
        cx = x + col * (card_width + gap_x)
        cy = y + row * (card_height + gap_y)
        hfill = card.get("fill", default_header_fill)
        hstroke = card.get("stroke", default_header_stroke)
        title = card.get("title", "")
        body = card.get("body", "")

        # Card outer border
        outer_id = f"card_{seed}_outer_{i}"
        outer = _rect(outer_id, cx, cy, card_width, card_height, seed, "#ffffff", hstroke, stroke_width=2)
        outer["strokeStyle"] = stroke_style
        outer["roundness"] = {"type": 3}
        elements.append(outer)
        seed += 1

        # Header strip
        hdr_id = f"card_{seed}_hdr_{i}"
        hdr = _rect(hdr_id, cx, cy, card_width, header_height, seed, hfill, hstroke, stroke_width=0)
        hdr["roundness"] = None
        elements.append(hdr)
        seed += 1

        # Header text (bound)
        hdr_t_id = f"card_{seed}_hdr_t_{i}"
        tw = len(title) * 9
        hdr_t = _text(hdr_t_id, cx + (card_width - tw) // 2, cy + (header_height - 20) // 2,
                       tw, 20, title, seed, color="#ffffff", font_size=16, text_align="center")
        hdr_t["containerId"] = hdr_id
        hdr["boundElements"] = [{"id": hdr_t_id, "type": "text"}]
        elements.append(hdr_t)
        seed += 1

        # Body text (free-floating below header)
        body_y = cy + header_height + 12
        body_h = card_height - header_height - 24
        body_w = card_width - 24
        body_t = _text(f"card_{seed}_body_{i}", cx + 12, body_y, body_w, body_h,
                        body, seed, color=DETAIL_COLOR, font_size=13, text_align="left")
        elements.append(body_t)
        seed += 1

    return elements


def grid_table(
    x: int,
    y: int,
    headers: list[str],
    rows: list[list[str]],
    col_width: int = 200,
    row_height: int = 50,
    header_height: int = 50,
    seed_base: int = 850000,
    header_fill: str = PRIMARY_FILL,
    header_stroke: str = PRIMARY_STROKE,
    cell_fill: str = "#f8fafc",
    cell_stroke: str = "#cbd5e1",
    header_text_color: str = "#ffffff",
    cell_text_color: str = DETAIL_COLOR,
    title: str = "",
    stroke_style: str = "solid",
) -> list[dict[str, Any]]:
    """Generate a visual grid/table as Excalidraw elements.

    Returns a list of rectangles (cells) + text labels arranged as a table
    with colored header row and alternating-feel body rows.

    Args:
        headers: column header labels
        rows: list of row data, each row is list[str] matching len(headers)
        col_width: width per column
        row_height: height per body row
        header_height: height of header row
        stroke_style: "solid", "dashed", or "dotted" for cell borders

    Example:
        grid_table(80, 200, ["Model", "Speed", "Cost"],
                   [["Opus", "slow", "$$$"], ["Haiku", "fast", "$"]],
                   col_width=180)
    """
    elements: list[dict[str, Any]] = []
    seed = seed_base
    n_cols = len(headers)
    n_rows = len(rows)
    total_w = n_cols * col_width
    total_h = header_height + n_rows * row_height

    if title:
        tw = len(title) * 10
        elements.append(_text(
            f"grid_{seed}_title", x, y - 40, tw, 30, title, seed,
            color=TITLE_COLOR, font_size=22, text_align="left",
        ))
        seed += 1

    for c, hdr in enumerate(headers):
        cx = x + c * col_width
        rect_id = f"grid_{seed}_hdr_{c}"
        seed += 1
        text_id = f"grid_{seed}_hdr_t_{c}"
        rect_el = _rect(
            rect_id, cx, y, col_width, header_height,
            seed - 1, header_fill, header_stroke, stroke_width=2,
        )
        rect_el["boundElements"] = [{"id": text_id, "type": "text"}]
        elements.append(rect_el)
        tw, th = len(hdr) * 8, 20
        text_el = _text(
            text_id,
            cx + (col_width - tw) // 2, y + (header_height - th) // 2,
            tw, th, hdr, seed,
            color=header_text_color, font_size=15, text_align="center",
        )
        text_el["containerId"] = rect_id
        elements.append(text_el)
        seed += 1

    for r, row_data in enumerate(rows):
        ry = y + header_height + r * row_height
        bg = cell_fill if r % 2 == 0 else "#ffffff"
        for c, cell_val in enumerate(row_data):
            cx = x + c * col_width
            rect_id = f"grid_{seed}_cell_{r}_{c}"
            seed += 1
            text_id = f"grid_{seed}_cell_t_{r}_{c}"
            el = _rect(
                rect_id, cx, ry, col_width, row_height,
                seed - 1, bg, cell_stroke, stroke_width=1,
            )
            el["strokeStyle"] = stroke_style
            el["boundElements"] = [{"id": text_id, "type": "text"}]
            elements.append(el)
            tw, th = len(cell_val) * 7, 18
            text_el = _text(
                text_id,
                cx + (col_width - tw) // 2, ry + (row_height - th) // 2,
                tw, th, cell_val, seed,
                color=cell_text_color, font_size=14, text_align="center",
            )
            text_el["containerId"] = rect_id
            elements.append(text_el)
            seed += 1

    return elements


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    sample = [("Sonnet", 3.0), ("Haiku", 0.8), ("Opus", 15.0)]
    elements = bar_chart(
        100,
        100,
        600,
        300,
        sample,
        title="Sample bar chart",
        y_label="$ / 1M tok",
    )
    print(f"bar_chart elements: {len(elements)}")
    if elements:
        print("first element keys:", sorted(elements[0].keys()))
        print("first element type:", elements[0].get("type"))

    line_els = line_chart(
        100,
        500,
        600,
        300,
        [("Q1", 0.91), ("Q2", 0.92), ("Q3", 0.78), ("Q4", 0.85)],
        title="Sample line chart",
        y_label="accuracy",
    )
    print(f"line_chart elements: {len(line_els)}")

    pie_els = pie_slice_approximation(400, 900, 200, sample)
    print(f"pie_slice_approximation (stacked bar) elements: {len(pie_els)}")

    grouped = grouped_bar_chart(0, 0, 800, 400, {
        "Claude": [("Speed", 8), ("Quality", 9), ("Cost", 3)],
        "GPT": [("Speed", 7), ("Quality", 8), ("Cost", 5)],
    }, title="Model Comparison")
    print(f"grouped_bar_chart elements: {len(grouped)}")

    annotated = add_annotation([], "Note: costs are relative", 100, 500)
    print(f"add_annotation elements: {len(annotated)}")

    table = grid_table(0, 0, ["Model", "Speed", "Cost"],
                       [["Opus", "slow", "$$$"], ["Sonnet", "medium", "$$"], ["Haiku", "fast", "$"]],
                       col_width=180, title="LLM Comparison Grid")
    print(f"grid_table elements: {len(table)}")

    cards = card_grid(0, 0, [
        {"title": "Opus 4.7", "body": "Best reasoning\nSlowest, most expensive\nUse for hard tasks"},
        {"title": "Sonnet 4.6", "body": "Balanced speed/quality\nGood default choice\nFast mode available", "fill": "#047857", "stroke": "#065f46"},
        {"title": "Haiku 4.5", "body": "Fastest, cheapest\nGood for classification\nHigh throughput", "fill": "#c2410c", "stroke": "#7c2d12"},
    ], cols=3, card_width=280, card_height=160)
    print(f"card_grid elements: {len(cards)}")
