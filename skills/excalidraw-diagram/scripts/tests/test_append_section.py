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
