# Visual Patterns

Choose a pattern that mirrors what the concept does.

## Pattern Map

| Concept behavior | Pattern |
|---|---|
| One source creates many outputs | Fan-out |
| Many inputs combine into one result | Convergence |
| Ordered steps over time | Timeline |
| Parent-child structure | Tree |
| Input becomes output | Assembly line |
| Two alternatives or before/after | Side-by-side |
| Continuous improvement | Cycle |
| Fuzzy context or memory | Cloud |
| Comparable items with shared fields | Grid or table |

## Fan-Out

Central source with arrows radiating to multiple targets. Use for PRDs producing deliverables, one agent dispatching tools, or one event source feeding multiple consumers.

## Convergence

Multiple inputs point into one synthesis or result. Use for aggregation, review, routing, decision-making, or evidence collection.

## Timeline

A line with dots and free-floating labels. Use for protocols, event streams, lifecycles, release phases, or tutorial steps. Prefer real event names over generic step labels.

## Tree

Lines plus free-floating text. Use for file systems, hierarchical tasks, taxonomies, or nested responsibilities. Avoid boxes for every node.

## Assembly Line

Input artifacts flow through transformation stages into output artifacts. Show what each artifact looks like: markdown, JSON, screenshot, PNG, video, etc.

## Side-By-Side

Two parallel structures with visible contrast. Use for old/new, option A/B, manual/automated, baseline/improved, or tradeoff comparisons.

## Grids And Tables

Use card grids or tables when 3+ items share the same attributes and the viewer needs to scan or compare them.

Do not use a uniform card grid as the entire visual argument. A grid is useful as one section alongside timelines, flows, evidence blocks, or comparisons.

Use `scripts/charts.py::card_grid()` for styled cards and `scripts/charts.py::grid_table()` for structured rows and columns.

## Evidence Artifacts

Evidence artifacts make technical diagrams teachable:

- Code snippets: use `scripts/charts.py::code_block()` when syntax highlighting matters.
- JSON/data: show real payload shapes or schemas.
- Event sequences: show actual event names.
- UI mockups: show what the user or system sees.
- Input/output samples: show concrete transformations.

For large technical diagrams, build one section at a time and merge with `scripts/append_section.py` if needed.
