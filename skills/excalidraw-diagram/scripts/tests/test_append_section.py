"""Regression tests for append_section.py."""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from append_section import _validate_section, main


def test_validate_section_rejects_duplicate_ids():
    with pytest.raises(SystemExit):
        _validate_section([
            {"id": "dup", "type": "rectangle"},
            {"id": "dup", "type": "text"},
        ])


def test_main_renames_base_id_collision(tmp_path):
    base = tmp_path / "base.excalidraw"
    section = tmp_path / "section.json"
    base.write_text(json.dumps({
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": [{"id": "a", "type": "rectangle", "x": 0, "y": 0, "width": 10, "height": 10, "seed": 1}],
        "appState": {},
        "files": {},
    }), encoding="utf-8")
    section.write_text(json.dumps([
        {"id": "a", "type": "text", "x": 0, "y": 20, "width": 10, "height": 10, "seed": 2},
    ]), encoding="utf-8")

    assert main([str(base), str(section)]) == 0
    data = json.loads(base.read_text(encoding="utf-8"))
    ids = [el["id"] for el in data["elements"]]
    assert ids == ["a", "a_2"]


@pytest.mark.parametrize("reverse_order", [False, True])
def test_main_reserves_incoming_ids_and_preserves_bindings(tmp_path, reverse_order):
    base = tmp_path / "base.excalidraw"
    section = tmp_path / "section.json"
    original = {"id": "box", "type": "rectangle"}
    base.write_text(json.dumps({"elements": [original]}), encoding="utf-8")
    incoming = [
        {"id": "box", "type": "rectangle", "boundElements": [{"id": "box_2", "type": "text"}]},
        {"id": "box_2", "type": "text", "containerId": "box"},
    ]
    if reverse_order:
        incoming.reverse()
    section.write_text(json.dumps(incoming), encoding="utf-8")

    assert main([str(base), str(section)]) == 0
    merged = json.loads(base.read_text(encoding="utf-8"))["elements"]
    assert merged[0] == original
    assert sorted(el["id"] for el in merged) == ["box", "box_2", "box_3"]
    by_id = {el["id"]: el for el in merged}
    assert by_id["box_2"]["containerId"] == "box_3"
    assert by_id["box_3"]["boundElements"] == [{"id": "box_2", "type": "text"}]
