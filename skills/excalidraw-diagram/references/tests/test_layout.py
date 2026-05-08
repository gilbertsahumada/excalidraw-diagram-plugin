"""Regression tests for layout.py coordinate helpers."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from layout import fan_out, timeline, tree, side_by_side, section, stack, estimate_text_size


def test_fan_out_returns_n_points():
    """fan_out returns exactly n points, each a tuple of 2 ints."""
    points = fan_out((500, 500), 4, 200)
    assert len(points) == 4
    for pt in points:
        assert isinstance(pt, tuple)
        assert len(pt) == 2
        assert isinstance(pt[0], int)
        assert isinstance(pt[1], int)


def test_timeline_evenly_spaced():
    """timeline returns 5 points: first at x_start, last at x_end, all same y."""
    points = timeline(400, 100, 700, 5)
    assert len(points) == 5
    # first point at x_start
    assert points[0][0] == 100
    # last point at x_end
    assert points[-1][0] == 700
    # all same y
    for pt in points:
        assert pt[1] == 400


def test_tree_has_trunk_and_branches():
    """tree result has 'trunk' and 'branches' keys; branches count matches n_branches."""
    result = tree((500, 100), 3, level_height=80, branch_width=40)
    assert "trunk" in result
    assert "branches" in result
    assert len(result["branches"]) == 3


def test_side_by_side_non_overlapping():
    """Left rectangle does not overlap right rectangle."""
    result = side_by_side(100, 600, 200, 400, 300)
    left = result["left"]
    right = result["right"]
    # left.x + left.w should be <= right.x (no overlap)
    assert left["x"] + left["w"] <= right["x"]


def test_section_next_y_increases():
    """next_y should be greater than y_start."""
    result = section(0, 100, 400)
    assert result["next_y"] > 100


def test_stack_vertical_no_overlap():
    """Each stacked item's y + h should be <= the next item's y."""
    items = stack((100, 100), [(200, 50), (200, 50), (200, 50)], gap=10)
    assert len(items) == 3
    for i in range(len(items) - 1):
        assert items[i]["y"] + items[i]["h"] <= items[i + 1]["y"]


def test_estimate_text_size_single_line():
    """estimate_text_size returns (int, int) with width > 0 and height > 0."""
    result = estimate_text_size("hello world", 16, 3)
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], int)
    assert isinstance(result[1], int)
    assert result[0] > 0
    assert result[1] > 0
