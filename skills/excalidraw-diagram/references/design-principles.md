# Design Principles

## Core Philosophy

Diagrams should argue, not display. A useful diagram shows relationships, causality, and transformation that text alone cannot express.

Use two tests before drawing:

- Isomorphism: if text disappeared, would the structure still communicate the concept?
- Education: can the viewer learn concrete mechanics, formats, or examples from the diagram?

## Depth Assessment

Use a simple/conceptual diagram when explaining a mental model, philosophy, or abstraction where specifics are not the point.

Use a comprehensive/technical diagram when diagramming a real system, protocol, workflow, or tutorial. Technical diagrams must include evidence artifacts such as code snippets, JSON/data examples, real event names, UI mockups, or concrete input/output examples.

## Multi-Zoom Architecture

Comprehensive diagrams should usually show three zoom levels:

- Summary flow: the whole pipeline at a glance.
- Section boundaries: visual regions grouped by responsibility, phase, actor, or system layer.
- Detail inside sections: evidence artifacts and concrete examples.

## Container Discipline

Default to free-floating text. Add a container only when it represents a distinct thing, carries meaning, groups related elements, or needs arrows to connect to it.

Good container uses:

- Process, action, decision, state, input, output, system, service.
- Evidence artifact background.
- UI mockup surface.

Avoid containers for section titles, annotations, captions, descriptions, and labels that typography can handle.

Aim for less than 30% of text elements inside containers.

## Bound Text Pattern

Text inside a shape must be centered and bound:

- The shape has `boundElements: [{"id": "text_id", "type": "text"}]`.
- The text has `containerId: "shape_id"`.
- The text uses `textAlign: "center"` and `verticalAlign: "middle"`.
- The text bbox height is close to the actual text height, then manually y-centered inside the shape.
- The text bbox width may match the container width for horizontal centering.

Use `scripts/layout.py::estimate_text_size()` to calculate bbox height.

## Shape Meaning

- Free text: labels, descriptions, metadata, annotations.
- Ellipse: start, end, source, sink, external actor.
- Rectangle: process, action, service, artifact.
- Diamond: decision or condition.
- Small ellipse/dot: timeline marker or anchor.
- Line: structure, tree trunk, timeline, divider, spine.
- Arrow: direction, flow, dependency.

## Aesthetic Defaults

- `fontFamily: 3`.
- `roughness: 0` for professional/technical diagrams unless hand-drawn is requested.
- `opacity: 100`; use color and size for hierarchy instead of transparency.
- Use free-floating titles and captions instead of cards around section text.
- Keep text readable at exported PNG size.
