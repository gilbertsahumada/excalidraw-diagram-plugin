# Element Templates

Copy-paste JSON templates for each Excalidraw element type. The `strokeColor` and `backgroundColor` values are placeholders — always pull actual colors from `color-palette.md` based on the element's semantic purpose.

## Free-Floating Text (no container)
```json
{
  "type": "text",
  "id": "label1",
  "x": 100, "y": 100,
  "width": 200, "height": 25,
  "text": "Section Title",
  "originalText": "Section Title",
  "fontSize": 20,
  "fontFamily": 3,
  "textAlign": "left",
  "verticalAlign": "top",
  "strokeColor": "<title color from palette>",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 11111,
  "version": 1,
  "versionNonce": 22222,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "containerId": null,
  "lineHeight": 1.25
}
```

## Line (structural, not arrow)
```json
{
  "type": "line",
  "id": "line1",
  "x": 100, "y": 100,
  "width": 0, "height": 200,
  "strokeColor": "<structural line color from palette>",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 44444,
  "version": 1,
  "versionNonce": 55555,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "points": [[0, 0], [0, 200]]
}
```

## Small Marker Dot
```json
{
  "type": "ellipse",
  "id": "dot1",
  "x": 94, "y": 94,
  "width": 12, "height": 12,
  "strokeColor": "<marker dot color from palette>",
  "backgroundColor": "<marker dot color from palette>",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 66666,
  "version": 1,
  "versionNonce": 77777,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false
}
```

## Rectangle
```json
{
  "type": "rectangle",
  "id": "elem1",
  "x": 100, "y": 100, "width": 180, "height": 90,
  "strokeColor": "<stroke from palette based on semantic purpose>",
  "backgroundColor": "<fill from palette based on semantic purpose>",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 12345,
  "version": 1,
  "versionNonce": 67890,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": [{"id": "text1", "type": "text"}],
  "link": null,
  "locked": false,
  "roundness": {"type": 3}
}
```

## Text centered inside a shape (REQUIRED pattern)

**RULE**: text inside a rectangle/ellipse/diamond MUST be centered both axes.

**The text's own bbox must match the rendered text size — NOT the container's size.** Then offset y so the text bbox is vertically centered inside the container. Excalidraw 0.18.x glues glyphs to the TOP of their bbox when bbox is much taller than text; `verticalAlign:"middle"` does not save you.

Use `estimate_text_size(text, fontSize, fontFamily)` from `references/layout.py` to compute the text bbox. Then:

```python
text_w, text_h = estimate_text_size(label, font_size=16, font_family=3)
text_x = container_x                                  # span container width
text_y = container_y + (container_h - text_h) // 2    # vertical center
text_width  = container_w
text_height = text_h
```

```json
// container (the shape) — 180×90 at (100,100)
{
  "type": "rectangle",
  "id": "elem1",
  "x": 100, "y": 100, "width": 180, "height": 90,
  "boundElements": [{"id": "text1", "type": "text"}],
  "...": "rest of fields per Rectangle template"
}

// text — own height (~23 for fontSize 16), y offset to center inside container
{
  "type": "text",
  "id": "text1",
  "x": 100, "y": 134, "width": 180, "height": 23,
  "text": "Process",
  "originalText": "Process",
  "fontSize": 16,
  "fontFamily": 3,
  "textAlign": "center",
  "verticalAlign": "middle",
  "strokeColor": "<text color from palette>",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 11111,
  "version": 1,
  "versionNonce": 22222,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "containerId": "elem1",
  "lineHeight": 1.25
}
```

### What NOT to do

```json
// WRONG #1 — text bbox = container bbox → glyphs glue to top of container
{
  "type": "text",
  "x": 100, "y": 100, "width": 180, "height": 90,  // ❌ height matches container
  "verticalAlign": "middle"                          // ignored when bbox >> text
}

// WRONG #2 — not bound, text floats over shape
{
  "type": "text",
  "containerId": null,  // ❌
  "x": 130, "y": 132    // ❌ manual offset, drifts
}

// WRONG #3 — alignments off
{
  "textAlign": "left",       // ❌ must be "center"
  "verticalAlign": "top"     // ❌ must be "middle"
}
```

If you need 2 text elements inside one shape (title + body), only one can be the container's bound text. The other belongs OUTSIDE the shape as free-floating text below it.

## Arrow
```json
{
  "type": "arrow",
  "id": "arrow1",
  "x": 282, "y": 145, "width": 118, "height": 0,
  "strokeColor": "<arrow color — typically matches source element's stroke from palette>",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 33333,
  "version": 1,
  "versionNonce": 44444,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "points": [[0, 0], [118, 0]],
  "startBinding": {"elementId": "elem1", "focus": 0, "gap": 2},
  "endBinding": {"elementId": "elem2", "focus": 0, "gap": 2},
  "startArrowhead": null,
  "endArrowhead": "arrow"
}
```

For curves: use 3+ points in `points` array.

## Reference Tables

**fontFamily values:**

| Value | Font | When |
|-------|------|------|
| 1 | Virgil (hand-drawn) | Brainstorm/informal feel |
| 2 | Helvetica (sans-serif) | Clean modern UI mockups |
| 3 | Cascadia Code (monospace) | Default — labels, code, paths |

**roundness values:**

| Value | Effect |
|-------|--------|
| `null` | Sharp corners |
| `{"type": 2}` | Default for ellipse |
| `{"type": 3}` | Rounded rectangle |

**textAlign / verticalAlign valid values:**
- textAlign: `"left"`, `"center"`, `"right"`
- verticalAlign: `"top"`, `"middle"`, `"bottom"`

**strokeStyle / fillStyle:**
- strokeStyle: `"solid"`, `"dashed"`, `"dotted"`
- fillStyle: `"solid"`, `"hachure"`, `"cross-hatch"`, `"zigzag"`
