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


# ---------------------------------------------------------------------------
# file_tree tests
# ---------------------------------------------------------------------------


def test_file_tree_returns_elements():
    """file_tree returns 1 bg rect + N text spans for a small tree."""
    from charts import file_tree
    tree = [
        ("project/", [
            ("src/", [
                ("main.py", "# entry point"),
                ("util.py", None),
            ]),
            ("README.md", None),
        ]),
    ]
    result = file_tree(80, 80, tree, font_size=14, theme_name="dark")
    assert isinstance(result, list)
    # 1 bg + at least 1 span per row (5 rows here, more spans where comments exist)
    assert len(result) >= 6
    assert result[0].get("type") == "rectangle"
    assert all(el.get("type") in {"rectangle", "text"} for el in result)


def test_file_tree_folder_color_differs_from_file_color():
    """Folder names render in a different color than file names."""
    from charts import file_tree
    tree = [("project/", [("README.md", None)])]
    result = file_tree(0, 0, tree, theme_name="dark")
    name_spans = [el for el in result if "_name" in el.get("id", "")]
    colors = {el["text"]: el["strokeColor"] for el in name_spans}
    assert colors["project/"] != colors["README.md"]


def test_file_tree_rejects_invalid_payload():
    """Folder with non-list payload raises ValueError."""
    from charts import file_tree
    with pytest.raises(ValueError):
        file_tree(0, 0, [("bad/", "not a list")])
