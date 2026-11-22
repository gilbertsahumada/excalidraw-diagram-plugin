---
name: excalidraw-diagram
description: Create, edit, render, or validate Excalidraw `.excalidraw` diagrams that make visual arguments. Use when the user explicitly asks for an Excalidraw artifact, diagram JSON, rendered diagram, or visual workflow/architecture/concept map. Do not use for generic explanations unless a visual artifact is requested.
---

# Excalidraw Diagram Creator

Create `.excalidraw` JSON diagrams that argue visually, render them, inspect the PNG, and fix defects before delivery.

## Quick Workflow

Start the canvas with the diagram itself. By default omit the title, kicker, subtitle and footer. Keep text next to the element it explains: a name, a value, a decision or a change. Include framing copy only if the user asks for it. Use the [compact Company Brain diagram](examples/company-brain.excalidraw) as the reference for text density.

1. Identify the viewer's question and the object they can follow to answer it. Choose a composition for the viewing context using [Illustrated explanations](references/design-principles.md#illustrated-explanations). A diagram for YouTube is a static editable canvas and PNG unless motion is requested.
2. Read `references/color-palette.md` before choosing colors.
3. For technical diagrams, research actual formats, event names, APIs, and payloads before drawing.
4. Pick visual patterns from `references/patterns.md`; avoid uniform box grids as the whole diagram.
5. Generate JSON with valid Excalidraw v2 structure.
6. Run `scripts/lint.py`, fix issues, then render with `scripts/render_excalidraw.py`.
7. View the PNG with the available image/browser tool and repeat until the diagram is readable and balanced.

## Reference Router

Read only what the task needs:

- `references/design-principles.md`: visual argument philosophy, depth assessment, containers, shape meaning, text rules.
- `references/patterns.md`: fan-out, convergence, timeline, tree, assembly line, side-by-side, grids, and examples.
- `references/color-palette.md`: single source of truth for light/dark colors and evidence artifact colors.
- `references/element-templates.md`: copy-paste Excalidraw element JSON templates.
- `references/json-schema.md`: Excalidraw wrapper, element fields, text fields, bindings, files.
- `references/render-validate.md`: lint/render/view/fix loop, first-time setup, local renderer bundle.
- `references/tooling.md`: `layout.py`, `charts.py`, `append_section.py`, `lint.py`, `render_excalidraw.py`.

## Hard Rules

- Default to free-floating text. Use containers only when the shape itself represents a thing, decision, state, or process.
- Bind a shape's centered label with `containerId` and the reciprocal `boundElements` entry. In an illustrated interface, group independently positioned content (such as message text and a typing indicator) with its surface so the composition moves together.
- For technical diagrams, include evidence artifacts: code, JSON/data shapes, event names, UI mockups, or concrete input/output examples.
- Do not invent colors. Use `references/color-palette.md`.
- Do not delegate full diagram generation to a sub-agent unless you also pass this skill's rules and validation requirements.
- Do not write ad hoc generator scripts for one-off JSON unless the diagram is too large to safely author by hand. Prefer bundled helpers in `scripts/`.

## Commands

From the skill directory:

```bash
cd skills/excalidraw-diagram
python3 scripts/lint.py path/to/file.excalidraw
python3 scripts/render_excalidraw.py path/to/file.excalidraw
```

If dependencies are not installed:

```bash
cd skills/excalidraw-diagram/scripts
uv sync --extra dev
uv run playwright install chromium
```

To rebuild the local Excalidraw renderer bundle after dependency changes:

```bash
yarn skill:bundle-renderer
```

## Delivery Checklist

- The `.excalidraw` file is valid JSON with `type`, `version`, `source`, `elements`, `appState`, and `files`.
- Lint has no unexpected issues.
- The PNG was rendered and visually inspected.
- Remove any label whose absence leaves the diagram equally clear.
- Text is legible, not clipped, and not overlapping.
- Arrows connect clearly and avoid crossing through primary content.
- Technical diagrams include concrete evidence artifacts.
- The final response names the generated `.excalidraw` and PNG paths.
