# Excalidraw Diagram Skill

A coding-agent skill for creating, rendering, and validating Excalidraw diagrams that make visual arguments.

## Setup

Install Python renderer dependencies:

```bash
cd skills/excalidraw-diagram/scripts
uv sync --extra dev
uv run playwright install chromium
```

Build the local Excalidraw renderer bundle from the repo root:

```bash
yarn skill:bundle-renderer
```

## Usage

Ask for an Excalidraw artifact, for example:

> Create an Excalidraw diagram showing how an AI coding agent plans, calls tools, validates, and reports results.

The skill should:

1. Read the palette and relevant references.
2. Generate `.excalidraw` JSON.
3. Run `scripts/lint.py`.
4. Render with `scripts/render_excalidraw.py`.
5. Inspect the PNG and fix defects.

## Structure

```text
excalidraw-diagram/
  SKILL.md
  agents/openai.yaml
  assets/
    render_template.html
    renderer-entry.js
    renderer-bundle.js
    excalidraw-assets/
  examples/
  evaluation/
  references/
    color-palette.md
    design-principles.md
    element-templates.md
    json-schema.md
    patterns.md
    render-validate.md
    tooling.md
  scripts/
    append_section.py
    charts.py
    layout.py
    lint.py
    render_excalidraw.py
    tests/
```

## Customization

Edit `references/color-palette.md` to change the visual style. Keep all color values there so diagrams stay consistent.
