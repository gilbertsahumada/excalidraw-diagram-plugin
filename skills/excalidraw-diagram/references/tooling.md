# Tooling

All executable helpers live in `scripts/`.

## `layout.py`

Coordinate helpers:

- `fan_out(center, n, radius, angle_span, start_angle)`
- `timeline(y, x_start, x_end, n)`
- `tree(root_xy, n_branches, level_height, branch_width)`
- `side_by_side(left_x, right_x, y, width, height)`
- `section(index, y_start, content_height)`
- `stack(start_xy, item_sizes, direction, gap)`
- `grid(x, y, cols, rows, cell_width, cell_height, gap_x, gap_y)`
- `estimate_text_size(text, font_size, font_family)`

Use these for patterns with more than two elements or when bound text needs reliable bbox height.

## `charts.py`

Element generators:

- `bar_chart()`, `grouped_bar_chart()`, `line_chart()`
- `pie_slice_approximation()` for pie-like proportions as a stacked bar
- `card_grid()` and `grid_table()`
- `code_block()` for syntax-highlighted evidence artifacts
- `file_tree()` for directory structures

Pass distinct `seed_base` values when composing multiple helper outputs.

## `lint.py`

Static analyzer for `.excalidraw` files:

- required fields
- overlap
- text overflow
- dangling arrows
- text centering/bindings
- container ratio

Run before every render.

## `append_section.py`

Merges a section JSON array into a base `.excalidraw` file. It namespaces seeds, handles ID collisions, and reports the next available y coordinate.

Use it for comprehensive diagrams built section-by-section.

## `render_excalidraw.py`

Renders `.excalidraw` JSON to PNG with Playwright and Excalidraw's official `exportToSvg()` utility through the local renderer bundle.
