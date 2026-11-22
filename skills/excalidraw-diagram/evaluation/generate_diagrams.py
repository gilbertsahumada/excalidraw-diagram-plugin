#!/usr/bin/env python3
"""Generate deterministic baseline/improved diagrams for skill evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PROMPTS = {
    "agent-workflow": (
        "Create a technical Excalidraw diagram showing an AI coding agent "
        "workflow: user intent, planner, tools, subagents, filesystem, tests, "
        "and final review. Include evidence artifacts that show a tool-call "
        "payload and a validation checklist."
    ),
    "streaming-lifecycle": (
        "Create a technical Excalidraw diagram showing a streaming lifecycle "
        "from agent to UI: request, run started, deltas, tool calls, UI updates, "
        "errors, and run finished. Use a timeline and concrete event names."
    ),
    "youtube-pipeline": (
        "Create a technical Excalidraw diagram showing a pipeline from YouTube "
        "script to scenes, prompts, Excalidraw diagrams, rendered PNGs, and video "
        "assembly. Show data shapes and validation gates."
    ),
}

COLORS = {
    "bg": "#ffffff",
    "title": "#1e40af",
    "subtitle": "#3b82f6",
    "body": "#64748b",
    "fill": "#3b82f6",
    "stroke": "#1e3a5f",
    "start_fill": "#fed7aa",
    "start_stroke": "#c2410c",
    "success_fill": "#a7f3d0",
    "success_stroke": "#047857",
    "decision_fill": "#fef3c7",
    "decision_stroke": "#b45309",
    "ai_fill": "#ddd6fe",
    "ai_stroke": "#6d28d9",
    "evidence_bg": "#1e293b",
    "evidence_dark_bg": "#020617",
    "evidence_text": "#22c55e",
}


def base(seed: int) -> dict:
    return {
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 0,
        "opacity": 100,
        "angle": 0,
        "seed": seed,
        "version": 1,
        "versionNonce": seed + 1,
        "isDeleted": False,
        "groupIds": [],
        "boundElements": None,
        "link": None,
        "locked": False,
    }


def text_size(text: str, font_size: int = 16) -> tuple[int, int]:
    lines = text.split("\n")
    width = max(1, max(len(line) for line in lines)) * font_size * 0.56
    height = len(lines) * font_size * 1.35
    return int(width) + 8, int(height) + 4


def text(eid: str, x: int, y: int, value: str, seed: int, *,
         size: int = 16, color: str | None = None, width: int | None = None,
         align: str = "left", valign: str = "top", container: str | None = None) -> dict:
    w, h = text_size(value, size)
    el = base(seed)
    el.update({
        "type": "text",
        "id": eid,
        "x": x,
        "y": y,
        "width": width or w,
        "height": h,
        "text": value,
        "originalText": value,
        "fontSize": size,
        "fontFamily": 3,
        "textAlign": align,
        "verticalAlign": valign,
        "strokeColor": color or COLORS["body"],
        "backgroundColor": "transparent",
        "containerId": container,
        "lineHeight": 1.25,
        "strokeWidth": 1,
    })
    return el


def rect(eid: str, x: int, y: int, w: int, h: int, seed: int, *,
         fill: str | None = None, stroke: str | None = None,
         bound: str | None = None, dashed: bool = False) -> dict:
    el = base(seed)
    el.update({
        "type": "rectangle",
        "id": eid,
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "strokeColor": stroke or COLORS["stroke"],
        "backgroundColor": fill or COLORS["fill"],
        "roundness": {"type": 3},
        "boundElements": [{"id": bound, "type": "text"}] if bound else None,
        "strokeStyle": "dashed" if dashed else "solid",
    })
    return el


def ellipse(eid: str, x: int, y: int, w: int, h: int, seed: int, *,
            fill: str | None = None, stroke: str | None = None, bound: str | None = None) -> dict:
    el = base(seed)
    el.update({
        "type": "ellipse",
        "id": eid,
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "strokeColor": stroke or COLORS["stroke"],
        "backgroundColor": fill or COLORS["fill"],
        "roundness": {"type": 2},
        "boundElements": [{"id": bound, "type": "text"}] if bound else None,
    })
    return el


def line(eid: str, x: int, y: int, pts: list[list[int]], seed: int, *,
         stroke: str | None = None, width: int = 2, dashed: bool = False) -> dict:
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    el = base(seed)
    el.update({
        "type": "line",
        "id": eid,
        "x": x,
        "y": y,
        "width": max(xs) - min(xs),
        "height": max(ys) - min(ys),
        "strokeColor": stroke or COLORS["stroke"],
        "backgroundColor": "transparent",
        "strokeWidth": width,
        "strokeStyle": "dashed" if dashed else "solid",
        "points": pts,
    })
    return el


def arrow(eid: str, x: int, y: int, pts: list[list[int]], seed: int, *,
          stroke: str | None = None, dashed: bool = False) -> dict:
    el = line(eid, x, y, pts, seed, stroke=stroke or COLORS["stroke"], dashed=dashed)
    el["type"] = "arrow"
    el["endArrowhead"] = "arrow"
    el["startArrowhead"] = None
    return el


def bound_label(box: dict, label_id: str, value: str, seed: int, *,
                size: int = 16, color: str = "#ffffff") -> dict:
    _, h = text_size(value, size)
    return text(
        label_id,
        int(box["x"]),
        int(box["y"] + (box["height"] - h) / 2),
        value,
        seed,
        size=size,
        color=color,
        width=int(box["width"]),
        align="center",
        valign="middle",
        container=str(box["id"]),
    )


def wrapper(elements: list[dict]) -> dict:
    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {"viewBackgroundColor": COLORS["bg"], "gridSize": 20},
        "files": {},
    }


def baseline_agent_workflow() -> list[dict]:
    els = [text("title", 60, 40, "AI coding agent workflow", 100, size=30, color=COLORS["title"])]
    boxes = [
        ("b_user", "User intent", 70, 160),
        ("b_plan", "Plan", 330, 160),
        ("b_tools", "Tools", 590, 160),
        ("b_files", "Filesystem", 330, 340),
        ("b_tests", "Tests", 590, 340),
        ("b_review", "Review", 850, 250),
    ]
    for i, (bid, label, x, y) in enumerate(boxes):
        tid = f"{bid}_text"
        box = rect(bid, x, y, 190, 90, 200 + i * 10, bound=tid)
        els += [box, bound_label(box, tid, label, 201 + i * 10)]
    els += [
        arrow("a1", 260, 205, [[0, 0], [70, 0]], 500),
        arrow("a2", 520, 205, [[0, 0], [70, 0]], 501),
        arrow("a3", 425, 250, [[0, 0], [0, 90]], 502),
        arrow("a4", 520, 385, [[0, 0], [70, 0]], 503),
        arrow("a5", 780, 385, [[0, 0], [70, -90]], 504),
        arrow("a6", 780, 205, [[0, 0], [70, 90]], 505),
        text("note", 70, 520, "Baseline: mostly equal boxes; evidence is implied, not shown.", 600, size=16),
    ]
    return els


def baseline_streaming_lifecycle() -> list[dict]:
    els = [text("title", 60, 40, "Agent to UI streaming lifecycle", 700, size=30, color=COLORS["title"])]
    labels = ["Request", "Start", "Delta", "Tool", "UI update", "Error", "Finish"]
    x0, y = 70, 220
    previous = None
    for i, label in enumerate(labels):
        bid = f"step_{i}"
        tid = f"step_{i}_text"
        x = x0 + i * 155
        box = rect(bid, x, y, 130, 80, 800 + i * 10, fill=COLORS["fill"], bound=tid)
        els += [box, bound_label(box, tid, label, 801 + i * 10, size=14)]
        if previous is not None:
            els.append(arrow(f"arr_{i}", previous + 130, y + 40, [[0, 0], [25, 0]], 900 + i))
        previous = x
    els.append(text("note", 70, 420, "Baseline: sequence exists, but real event payloads are missing.", 950, size=16))
    return els


def baseline_youtube_pipeline() -> list[dict]:
    els = [text("title", 60, 40, "YouTube script to Excalidraw pipeline", 1000, size=30, color=COLORS["title"])]
    labels = ["Script", "Scenes", "Prompts", "Diagrams", "PNGs", "Video"]
    for i, label in enumerate(labels):
        x = 80 + i * 175
        bid = f"pipe_{i}"
        tid = f"pipe_{i}_text"
        box = rect(bid, x, 220, 135, 90, 1100 + i * 10, bound=tid)
        els += [box, bound_label(box, tid, label, 1101 + i * 10)]
        if i:
            els.append(arrow(f"pipe_arrow_{i}", x - 40, 265, [[0, 0], [40, 0]], 1200 + i))
    els.append(text("note", 80, 430, "Baseline: no data shape, validation gate, or artifact examples.", 1300, size=16))
    return els


def evidence_block(eid: str, x: int, y: int, title: str, lines: list[str], seed: int,
                   *, dark: bool = True) -> list[dict]:
    bg = COLORS["evidence_dark_bg"] if dark else COLORS["evidence_bg"]
    width = max(260, max(len(line) for line in lines + [title]) * 9 + 34)
    height = 38 + len(lines) * 24 + 18
    els = [rect(f"{eid}_bg", x, y, width, height, seed, fill=bg, stroke="#334155")]
    els.append(text(f"{eid}_title", x + 16, y + 14, title, seed + 1, size=14, color="#cbd5e1"))
    for i, line_value in enumerate(lines):
        els.append(text(f"{eid}_line_{i}", x + 16, y + 46 + i * 24, line_value, seed + 10 + i, size=13, color=COLORS["evidence_text"]))
    return els


def improved_agent_workflow() -> list[dict]:
    els = [
        text("title", 60, 36, "AI coding agent workflow", 2000, size=30, color=COLORS["title"]),
        text("subtitle", 60, 82, "Plan -> act with tools -> verify -> report", 2001, size=16, color=COLORS["body"]),
    ]
    user = ellipse("user", 80, 170, 150, 70, 2010, fill=COLORS["start_fill"], stroke=COLORS["start_stroke"], bound="user_text")
    planner = rect("planner", 330, 145, 210, 120, 2020, fill=COLORS["ai_fill"], stroke=COLORS["ai_stroke"], bound="planner_text")
    review = ellipse("review", 920, 180, 170, 82, 2030, fill=COLORS["success_fill"], stroke=COLORS["success_stroke"], bound="review_text")
    els += [
        user, bound_label(user, "user_text", "User intent", 2011, color="#374151"),
        planner, bound_label(planner, "planner_text", "Planner\nchooses path", 2021, color="#374151"),
        review, bound_label(review, "review_text", "Final review", 2031, color="#374151"),
        arrow("user_to_planner", 230, 205, [[0, 0], [100, 0]], 2040, stroke=COLORS["start_stroke"]),
    ]
    tool_points = [(240, 390, "Filesystem"), (420, 430, "Tests"), (620, 390, "Browser/render"), (760, 430, "Subagents")]
    els.append(line("tool_spine", 300, 345, [[0, 0], [520, 0]], 2050, stroke=COLORS["ai_stroke"], dashed=True))
    for i, (x, y, label) in enumerate(tool_points):
        dot = ellipse(f"tool_dot_{i}", x, y, 16, 16, 2060 + i, fill=COLORS["fill"], stroke=COLORS["stroke"])
        els += [
            arrow(f"planner_to_tool_{i}", 435, 265, [[0, 0], [x - 435 + 8, y - 265 + 8]], 2070 + i, stroke=COLORS["ai_stroke"]),
            dot,
            text(f"tool_label_{i}", x - 28, y + 28, label, 2080 + i, size=14, color=COLORS["subtitle"], width=150, align="center"),
        ]
    els += [
        arrow("tools_to_review", 768, 438, [[0, 0], [152, -197]], 2090, stroke=COLORS["success_stroke"]),
        *evidence_block("payload", 600, 110, "tool call payload", ['{"tool":"exec_command",', ' "cmd":"python -m pytest"}'], 2100),
        *evidence_block("checklist", 80, 505, "validation checklist", ["lint: clean", "render: png viewed", "tests: passing"], 2150, dark=False),
    ]
    return els


def improved_streaming_lifecycle() -> list[dict]:
    els = [
        text("title", 60, 36, "Agent to UI streaming lifecycle", 3000, size=30, color=COLORS["title"]),
        line("timeline", 100, 240, [[0, 0], [920, 0]], 3010, stroke=COLORS["stroke"], width=3),
    ]
    events = [
        ("REQUEST", "user submits prompt"),
        ("RUN_STARTED", "server opens stream"),
        ("STATE_DELTA", "agent state changes"),
        ("TOOL_CALL", "tool execution"),
        ("UI_UPDATE", "partial render"),
        ("ERROR", "recover or abort"),
        ("RUN_FINISHED", "final message"),
    ]
    for i, (event, desc) in enumerate(events):
        x = 100 + i * 150
        fill = COLORS["decision_fill"] if event == "ERROR" else COLORS["fill"]
        stroke = COLORS["decision_stroke"] if event == "ERROR" else COLORS["stroke"]
        els += [
            ellipse(f"dot_{i}", x - 7, 233, 14, 14, 3020 + i, fill=fill, stroke=stroke),
            text(f"event_{i}", x - 58, 170 if i % 2 == 0 else 280, event, 3030 + i, size=14, color=COLORS["subtitle"], width=130, align="center"),
            text(f"desc_{i}", x - 68, 194 if i % 2 == 0 else 304, desc, 3040 + i, size=12, color=COLORS["body"], width=150, align="center"),
        ]
    els += [
        *evidence_block("event_payload", 100, 405, "stream event shape", ['{"type":"STATE_DELTA",', ' "path":["messages",2],', ' "delta":{"text":"..."}}'], 3100),
        rect("ui_mock", 690, 380, 330, 160, 3150, fill="#dbeafe", stroke="#1e40af", dashed=True),
        text("ui_title", 710, 350, "UI panel", 3151, size=15, color=COLORS["title"]),
        line("ui_bar_1", 710, 435, [[0, 0], [280, 0]], 3152, stroke=COLORS["subtitle"]),
        line("ui_bar_2", 710, 465, [[0, 0], [210, 0]], 3153, stroke=COLORS["body"]),
        line("ui_bar_3", 710, 495, [[0, 0], [250, 0]], 3154, stroke=COLORS["body"]),
    ]
    return els


def improved_youtube_pipeline() -> list[dict]:
    els = [
        text("title", 60, 36, "YouTube script to Excalidraw pipeline", 4000, size=30, color=COLORS["title"]),
        text("subtitle", 60, 82, "Each stage transforms a concrete artifact and gates quality before video assembly.", 4001, size=15, color=COLORS["body"]),
    ]
    stages = [
        ("Script", "markdown\nsections", COLORS["start_fill"], COLORS["start_stroke"]),
        ("Scenes", "timed\nbeats", "#dbeafe", "#1e40af"),
        ("Prompt", "visual\nbrief", COLORS["ai_fill"], COLORS["ai_stroke"]),
        ("Excalidraw", "json\nscene", COLORS["fill"], COLORS["stroke"]),
        ("Render", "png\nproof", COLORS["decision_fill"], COLORS["decision_stroke"]),
        ("Video", "final\nasset", COLORS["success_fill"], COLORS["success_stroke"]),
    ]
    for i, (label, detail, fill, stroke) in enumerate(stages):
        x = 70 + i * 175
        box = rect(f"stage_{i}", x, 190, 130, 86, 4010 + i, fill=fill, stroke=stroke, bound=f"stage_{i}_text")
        els += [
            box,
            bound_label(box, f"stage_{i}_text", label, 4020 + i, color="#374151"),
            text(f"stage_detail_{i}", x, 292, detail, 4030 + i, size=13, color=COLORS["body"], width=130, align="center"),
        ]
        if i:
            els.append(arrow(f"stage_arrow_{i}", x - 45, 233, [[0, 0], [45, 0]], 4040 + i, stroke=stroke))
    els += [
        *evidence_block("scene_json", 80, 420, "scene data", ['{"title":"Hook",', ' "duration":18,', ' "visual":"fan-out"}'], 4100),
        *evidence_block("render_gate", 455, 420, "quality gate", ["lint issues == 0", "png inspected", "text readable"], 4150, dark=False),
        *evidence_block("output", 760, 420, "output files", ["slide-01.excalidraw", "slide-01.png", "timeline.mp4"], 4200),
    ]
    return els


BUILDERS = {
    "baseline": {
        "agent-workflow": baseline_agent_workflow,
        "streaming-lifecycle": baseline_streaming_lifecycle,
        "youtube-pipeline": baseline_youtube_pipeline,
    },
    "improved": {
        "agent-workflow": improved_agent_workflow,
        "streaming-lifecycle": improved_streaming_lifecycle,
        "youtube-pipeline": improved_youtube_pipeline,
    },
}


def write_prompts() -> None:
    prompt_dir = ROOT / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    for name, prompt in PROMPTS.items():
        (prompt_dir / f"{name}.md").write_text(prompt + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("variant", choices=sorted(BUILDERS))
    args = parser.parse_args()
    write_prompts()
    out_dir = ROOT / args.variant
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, builder in BUILDERS[args.variant].items():
        output = out_dir / f"{name}.excalidraw"
        output.write_text(json.dumps(wrapper(builder()), indent=2), encoding="utf-8")
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
