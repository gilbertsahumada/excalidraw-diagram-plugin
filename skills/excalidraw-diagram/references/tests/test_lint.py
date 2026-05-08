"""Regression tests for lint.py static analyzer checks."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from lint import (
    check_overlap,
    check_text_overflow,
    check_dangling_arrows,
    check_container_ratio,
    check_missing_required_fields,
)


# ---------------------------------------------------------------------------
# Helpers: minimal element dicts
# ---------------------------------------------------------------------------


def _rect(id_, x, y, w, h, **kwargs):
    el = {"type": "rectangle", "id": id_, "x": x, "y": y, "width": w, "height": h}
    el.update(kwargs)
    return el


def _text(id_, x, y, w, h, text="hello", **kwargs):
    el = {
        "type": "text",
        "id": id_,
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "text": text,
        "fontSize": 16,
    }
    el.update(kwargs)
    return el


def _arrow(id_, x, y, points, start_binding=None, end_binding=None):
    return {
        "type": "arrow",
        "id": id_,
        "x": x,
        "y": y,
        "width": 100,
        "height": 0,
        "points": points,
        "startBinding": start_binding,
        "endBinding": end_binding,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_overlap_detects_overlapping_rects():
    """Two rects at the same position should produce 1 overlap warning."""
    elements = [
        _rect("a", 100, 100, 200, 200),
        _rect("b", 100, 100, 200, 200),
    ]
    warnings = check_overlap(elements)
    assert len(warnings) == 1
    assert warnings[0]["type"] == "overlap"


def test_overlap_skips_bound_pairs():
    """A rect + text with containerId pointing to the rect should produce 0 warnings."""
    elements = [
        _rect("container1", 100, 100, 200, 200, boundElements=[{"id": "text1"}]),
        _text("text1", 100, 100, 200, 200, containerId="container1"),
    ]
    warnings = check_overlap(elements)
    assert len(warnings) == 0


def test_overlap_skips_evidence_artifacts():
    """Rect with backgroundColor='#1e293b' + overlapping text should produce 0 warnings."""
    elements = [
        _rect("evidence1", 100, 100, 400, 300, backgroundColor="#1e293b"),
        _text("code1", 110, 110, 380, 280, text="some code"),
    ]
    warnings = check_overlap(elements)
    assert len(warnings) == 0


def test_text_overflow_warns_on_wide_text():
    """Text with 50 chars in a small container should produce at least 1 warning."""
    container = _rect("c1", 100, 100, 100, 100, boundElements=[{"id": "t1"}])
    text_el = _text("t1", 100, 100, 100, 20, text="x" * 50, containerId="c1")
    elements = [container, text_el]
    warnings = check_text_overflow(elements)
    assert len(warnings) >= 1
    assert warnings[0]["type"] == "text-overflow"


def test_dangling_arrow_detected():
    """Arrow with null bindings pointing to empty space should produce at least 1 warning."""
    # Arrow far from any element
    arrow = _arrow("arr1", 1000, 1000, [[0, 0], [200, 0]])
    # A rect that is far away
    rect = _rect("r1", 0, 0, 50, 50)
    elements = [rect, arrow]
    warnings = check_dangling_arrows(elements)
    assert len(warnings) >= 1
    assert warnings[0]["type"] == "dangling-arrow"


def test_container_ratio_warns_above_threshold():
    """4 text elements with 2 in containers (50%) exceeds default 0.30 threshold."""
    elements = [
        _text("t1", 0, 0, 100, 20, containerId="c1"),
        _text("t2", 0, 50, 100, 20, containerId="c2"),
        _text("t3", 0, 100, 100, 20),
        _text("t4", 0, 150, 100, 20),
    ]
    warnings = check_container_ratio(elements)
    assert len(warnings) == 1
    assert warnings[0]["type"] == "container-ratio"


def test_container_ratio_custom_threshold():
    """Same elements with max_ratio=0.6 should produce 0 warnings (50% < 60%)."""
    elements = [
        _text("t1", 0, 0, 100, 20, containerId="c1"),
        _text("t2", 0, 50, 100, 20, containerId="c2"),
        _text("t3", 0, 100, 100, 20),
        _text("t4", 0, 150, 100, 20),
    ]
    warnings = check_container_ratio(elements, max_ratio=0.6)
    assert len(warnings) == 0


def test_missing_fields_detected():
    """Element without 'type' should produce 1 warning."""
    elements = [
        {"id": "e1", "x": 0, "y": 0},  # missing 'type'
    ]
    warnings = check_missing_required_fields(elements)
    assert len(warnings) == 1
    assert warnings[0]["type"] == "missing-required"
