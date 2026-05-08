"""Coordinate-computing helpers for generating Excalidraw diagrams.

These functions return integer (x, y) coordinates (or dicts of them) for
common diagram patterns so agents do not have to compute layouts by hand.

Excalidraw convention: y grows downward, x grows rightward.
"""

from math import ceil
import math


def fan_out(center, n, radius, angle_span=180, start_angle=0):
    """Return n (x, y) points evenly distributed along an arc.

    angle_span and start_angle are in degrees. start_angle=0 points right
    (positive x); 90 points down (Excalidraw y grows downward); 270 points up.

    # Example: fan_out((500, 500), 4, 200, angle_span=180, start_angle=270)
    # → 4 points spread on an arc above the center (upper semicircle).
    """
    if n <= 0:
        return []
    cx, cy = center
    points = []
    if n == 1:
        # Place the single point at the middle of the arc.
        angle_deg = start_angle + angle_span / 2.0
        angle_rad = math.radians(angle_deg)
        x = int(round(cx + radius * math.cos(angle_rad)))
        y = int(round(cy + radius * math.sin(angle_rad)))
        return [(x, y)]
    step = angle_span / (n - 1)
    for i in range(n):
        angle_deg = start_angle + step * i
        angle_rad = math.radians(angle_deg)
        x = int(round(cx + radius * math.cos(angle_rad)))
        y = int(round(cy + radius * math.sin(angle_rad)))
        points.append((x, y))
    return points


def timeline(y, x_start, x_end, n):
    """Return n evenly-spaced (x, y) points along a horizontal line at y.

    Points span x_start through x_end inclusive.

    # Example: timeline(400, 100, 700, 4)
    # → [(100, 400), (300, 400), (500, 400), (700, 400)]
    """
    if n <= 0:
        return []
    if n == 1:
        return [(int(round((x_start + x_end) / 2.0)), y)]
    step = (x_end - x_start) / (n - 1)
    return [(int(round(x_start + step * i)), y) for i in range(n)]


def tree(root_xy, n_branches, level_height=80, branch_width=40):
    """Return a dict describing a vertical trunk with n horizontal branches.

    Output:
      {
        'trunk': {'x': int, 'y_start': int, 'y_end': int},
        'branches': [
          {
            'index': int,
            'horizontal_line': {'x_start': int, 'x_end': int, 'y': int},
            'dot': (x, y),
            'label_x': int,
          },
          ...
        ],
      }

    Branches alternate left/right. Even indices (0, 2, ...) extend right of
    the trunk, odd indices (1, 3, ...) extend left. Each branch is one
    level_height below the previous.

    # Example: tree((500, 100), 3, level_height=80, branch_width=40)
    # → trunk from y=100 to y=340 with 3 alternating branches.
    """
    trunk_x, root_y = root_xy
    branches = []
    for i in range(n_branches):
        branch_y = root_y + level_height * (i + 1)
        if i % 2 == 0:
            x_start = trunk_x
            x_end = trunk_x + branch_width
            dot = (x_end, branch_y)
            label_x = x_end + 10
        else:
            x_start = trunk_x - branch_width
            x_end = trunk_x
            dot = (x_start, branch_y)
            label_x = x_start - 10
        branches.append({
            'index': i,
            'horizontal_line': {'x_start': x_start, 'x_end': x_end, 'y': branch_y},
            'dot': dot,
            'label_x': label_x,
        })
    trunk_y_end = root_y + level_height * n_branches if n_branches > 0 else root_y
    return {
        'trunk': {'x': trunk_x, 'y_start': root_y, 'y_end': trunk_y_end},
        'branches': branches,
    }


def side_by_side(left_x, right_x, y, width, height):
    """Return two equal-sized rectangles side by side and the divider midpoint.

    Output:
      {
        'left':  {'x': int, 'y': int, 'w': int, 'h': int},
        'right': {'x': int, 'y': int, 'w': int, 'h': int},
        'divider_x': int,
      }

    # Example: side_by_side(100, 600, 200, 400, 300)
    # → left at x=100, right at x=600, divider at midpoint between them.
    """
    divider_x = int(round((left_x + width + right_x) / 2.0))
    return {
        'left': {'x': left_x, 'y': y, 'w': width, 'h': height},
        'right': {'x': right_x, 'y': y, 'w': width, 'h': height},
        'divider_x': divider_x,
    }


def section(index, y_start, content_height, title_size=36, divider_pad=20):
    """Return y-coordinates for a titled section block.

    Output:
      {
        'title_y':   y_start,
        'divider_y': y_start + title_size + divider_pad,
        'content_y': divider_y + 20,
        'next_y':    content_y + content_height + 40,
        'seed_base': index * 100000,
      }

    seed_base is suggested as a deterministic offset for any per-section
    randomness so sections don't collide.

    # Example: section(0, 100, 400)
    # → title at y=100, divider at y=156, content at y=176, next_y=616.
    """
    title_y = y_start
    divider_y = y_start + title_size + divider_pad
    content_y = divider_y + 20
    next_y = content_y + content_height + 40
    return {
        'title_y': title_y,
        'divider_y': divider_y,
        'content_y': content_y,
        'next_y': next_y,
        'seed_base': index * 100000,
    }


def stack(start_xy, item_sizes, direction="vertical", gap=20):
    """Return rectangle placements stacked from start_xy with a gap between items.

    item_sizes is a list of (width, height) tuples. direction is "vertical"
    (stack downward) or "horizontal" (stack rightward).

    Output: [{'x': int, 'y': int, 'w': int, 'h': int}, ...]

    # Example: stack((100, 100), [(200, 50), (200, 50), (200, 50)], gap=10)
    # → three boxes stacked vertically starting at (100, 100).
    """
    x0, y0 = start_xy
    out = []
    cx, cy = x0, y0
    for w, h in item_sizes:
        out.append({'x': cx, 'y': cy, 'w': w, 'h': h})
        if direction == "horizontal":
            cx += w + gap
        else:
            cy += h + gap
    return out


def grid(
    x: int, y: int,
    cols: int, rows: int,
    cell_width: int, cell_height: int,
    gap_x: int = 20, gap_y: int = 20,
) -> list[dict]:
    """Return a list of cell positions arranged in a rows × cols grid.

    Each cell is a dict: {'row': r, 'col': c, 'x': ..., 'y': ..., 'w': cell_width, 'h': cell_height}.
    Cells are ordered row-major (left-to-right, top-to-bottom).

    Example:
        grid(100, 200, cols=3, rows=2, cell_width=200, cell_height=100, gap_x=20, gap_y=20)
        # → 6 cells in a 3×2 grid starting at (100, 200)
    """
    cells = []
    for r in range(rows):
        for c in range(cols):
            cx = x + c * (cell_width + gap_x)
            cy = y + r * (cell_height + gap_y)
            cells.append({'row': r, 'col': c, 'x': cx, 'y': cy, 'w': cell_width, 'h': cell_height})
    return cells


def estimate_text_size(text: str, font_size: int = 15, font_family: int = 3) -> tuple[int, int]:
    """Estimate (width, height) in pixels for an Excalidraw text element.

    Uses per-fontFamily character-width multipliers:
      1 (Virgil/hand-drawn): 0.60 × fontSize per char
      2 (Helvetica/sans):    0.50 × fontSize per char
      3 (Cascadia/mono):     0.55 × fontSize per char (default)

    Height uses 1.4× fontSize per line (Excalidraw's default lineHeight=1.25
    plus padding).

    Note: lint.py has its own inline copy of these constants for standalone use.
    This function is the authoritative version.

    Example:
        estimate_text_size("hello world", 16, 3)
        # → (106, 23)  — 11 chars × 16 × 0.55 ≈ 97, rounded up; 1 line × 16 × 1.4 = 23
    """
    lines = text.split("\n")
    n_lines = max(len(lines), 1)
    max_chars = max((len(line) for line in lines), default=1)
    max_chars = max(max_chars, 1)
    multipliers = {1: 0.60, 2: 0.50, 3: 0.55}
    multiplier = multipliers.get(font_family, 0.55)
    width = ceil(max_chars * font_size * multiplier)
    height = ceil(n_lines * font_size * 1.4)
    return (width, height)


if __name__ == "__main__":
    print("fan_out:", fan_out((500, 500), 4, 200, angle_span=180, start_angle=270))
    print("timeline:", timeline(400, 100, 700, 4))
    print("tree:", tree((500, 100), 3, level_height=80, branch_width=40))
    print("side_by_side:", side_by_side(100, 600, 200, 400, 300))
    print("section:", section(0, 100, 400))
    print("stack:", stack((100, 100), [(200, 50), (200, 50), (200, 50)], gap=10))
    print("grid:", grid(100, 200, 3, 2, 200, 100, 20, 20))
    print("estimate_text_size:", estimate_text_size("hello world", 16, 3))
    print("estimate_text_size (multiline):", estimate_text_size("line one\nline two\nline three", 14, 3))
