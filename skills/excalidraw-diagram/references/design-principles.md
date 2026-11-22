# Design Principles

## Core Philosophy

Diagrams should argue, not display. A useful diagram shows relationships, causality, and transformation that text alone cannot express.

Use two tests before drawing:

- Isomorphism: if text disappeared, would the structure still communicate the concept?
- Education: can the viewer learn concrete mechanics, formats, or examples from the diagram?

## Illustrated explanations

Choose an object whose visible change carries the explanation. In a queue, follow one job as it waits, runs, and finishes. In a comparison, repeat the same input on both sides so the differing outcome is easy to spot. Draw recognizable silhouettes, marks, and labels with native editable elements. Reserve hand lettering for a focal detail such as the user's message; keep technical annotations in a readable face.

For **documentation**, give readers a path they can trace. Place the actors or stages in stable positions, attach a concrete value to the handoff, and branch at the condition that changes the outcome. The [streaming reference](../examples/streaming-documentation.excalidraw) uses two lifelines and follows the text into the client. A single-component lifecycle may need only a state path.

For **a presentation or YouTube diagram**, show what a viewer would actually recognize: a chat bubble, a file changing, a job moving through a queue. Give the starting state a focal position and use the remaining space to show the significant change. The [streaming chat](../examples/streaming-youtube.excalidraw) uses a typing indicator, check mark and retry control. Its layered surfaces give the chat depth; reuse that treatment where it helps distinguish foreground content. Pick light or dark for the intended setting.

Inspect the rendered canvas at its intended viewing size. Can you follow the object and distinguish outcomes even without color? Group each composite illustration for editing. When lint reports overlap, inspect the named elements: shadows behind a surface, indicator lights inside a server and controls inside a mockup can intentionally overlap. Fix collisions that obscure text, connectors or meaning.

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

For a centered shape label, use a reciprocal binding:

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
- Place essential labels at the relevant object or connector. In the Company Brain example, “Tú apruebas” identifies who authorizes publication, while CSV and PDF show what changed in the same issue.
- Keep text readable at exported PNG size.
