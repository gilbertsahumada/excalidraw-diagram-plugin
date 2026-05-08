"""Regression tests for charts.py element generators."""

import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from charts import bar_chart, line_chart


# ---------------------------------------------------------------------------
# bar_chart tests
# ---------------------------------------------------------------------------


def test_bar_chart_returns_elements():
    """bar_chart returns a non-empty list of dicts each with a 'type' key."""
    data = [("A", 10), ("B", 20), ("C", 30)]
    result = bar_chart(100, 100, 600, 300, data)
    assert isinstance(result, list)
    assert len(result) > 0
    for el in result:
        assert isinstance(el, dict)
        assert "type" in el


def test_bar_chart_has_correct_bar_count():
    """3 data points should produce exactly 3 rectangle elements for bars."""
    data = [("A", 10), ("B", 20), ("C", 30)]
    result = bar_chart(100, 100, 600, 300, data, seed_base=700000)
    # Bar elements have IDs like chart_700000_bar_0, chart_700000_bar_1, etc.
    bar_rects = [el for el in result if el.get("type") == "rectangle" and "_bar_" in el.get("id", "")]
    assert len(bar_rects) == 3


# ---------------------------------------------------------------------------
# line_chart tests
# ---------------------------------------------------------------------------


def test_line_chart_returns_elements():
    """line_chart returns a non-empty list."""
    data = [("Q1", 0.91), ("Q2", 0.92), ("Q3", 0.78), ("Q4", 0.85)]
    result = line_chart(100, 100, 600, 300, data)
    assert isinstance(result, list)
    assert len(result) > 0


def test_line_chart_has_line_element():
    """line_chart output includes at least one element with type 'line'."""
    data = [("Q1", 0.91), ("Q2", 0.92), ("Q3", 0.78), ("Q4", 0.85)]
    result = line_chart(100, 100, 600, 300, data)
    line_elements = [el for el in result if el.get("type") == "line"]
    assert len(line_elements) >= 1


# ---------------------------------------------------------------------------
# grouped_bar_chart (defensive — may not exist yet)
# ---------------------------------------------------------------------------


def test_grouped_bar_chart():
    """If grouped_bar_chart exists, verify it returns non-empty elements."""
    try:
        from charts import grouped_bar_chart
    except ImportError:
        pytest.skip("grouped_bar_chart not yet added")
    result = grouped_bar_chart(
        0, 0, 800, 400,
        {"A": [("x", 1), ("y", 2)], "B": [("x", 3), ("y", 4)]},
    )
    assert len(result) > 0
