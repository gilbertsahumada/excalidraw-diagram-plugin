# Render And Validate

You cannot judge an Excalidraw diagram from JSON alone. Always lint, render, view, and fix.

## Commands

From the skill directory:

```bash
python3 scripts/lint.py path/to/file.excalidraw
python3 scripts/render_excalidraw.py path/to/file.excalidraw
```

The renderer writes a PNG next to the `.excalidraw` file unless `--output` is provided.

## First-Time Setup

```bash
cd skills/excalidraw-diagram/scripts
uv sync --extra dev
uv run playwright install chromium
```

The render script uses Playwright and a local Excalidraw renderer bundle in `assets/renderer-bundle.js`.

If the local bundle is missing or stale, rebuild it from the repo root:

```bash
yarn skill:bundle-renderer
```

## Loop

1. Lint first. Fix unexpected overlap, overflow, broken bindings, dangling arrows, or excessive containers.
2. Render to PNG.
3. View the PNG with the available image/browser tool.
4. Check concept fit: does the structure match the intended argument?
5. Check visual defects: clipping, overlapping, ambiguous labels, arrow crossings, cramped sections, unreadable text.
6. Fix JSON and repeat.

## Stop Criteria

Stop only when:

- The diagram matches the intended visual story.
- Text is legible and not clipped.
- Arrows route cleanly and connect to the correct elements.
- Spacing is balanced.
- Technical diagrams contain concrete evidence artifacts.
- Lint has no unexpected issues.

Warnings can be accepted only when they are intentional and documented in the final note.
