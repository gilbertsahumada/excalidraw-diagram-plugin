# Excalidraw Skill Evaluation

Generated from the same three prompts before and after the skill improvements.

## Prompts

- `prompts/agent-workflow.md`
- `prompts/streaming-lifecycle.md`
- `prompts/youtube-pipeline.md`

## Results

| Diagram | Baseline lint | Improved lint | Baseline render | Improved render | Visual change |
|---|---:|---:|---|---|---|
| Agent workflow | 1 issue | 0 issues | PNG generated | PNG generated | Improved adds semantic shapes, tool fan-out, payload evidence, and validation checklist. |
| Streaming lifecycle | 1 issue | 0 issues | PNG generated | PNG generated | Improved uses a timeline, real event names, event payload, and UI mockup. |
| YouTube pipeline | 1 issue | 0 issues | PNG generated | PNG generated | Improved shows artifact transformations, validation gate, and concrete output files. |

## Baseline Issues

```text
agent-workflow.excalidraw - 1 issues
  [container-ratio] 6/8 text elements in containers (75% > 30%)
streaming-lifecycle.excalidraw - 1 issues
  [container-ratio] 7/9 text elements in containers (78% > 30%)
youtube-pipeline.excalidraw - 1 issues
  [container-ratio] 6/8 text elements in containers (75% > 30%)
```

## Improved Issues

```text
agent-workflow.excalidraw - 0 issues
streaming-lifecycle.excalidraw - 0 issues
youtube-pipeline.excalidraw - 0 issues
```

## Artifact Paths

Baseline:

- `baseline/agent-workflow.excalidraw`
- `baseline/streaming-lifecycle.excalidraw`
- `baseline/youtube-pipeline.excalidraw`

Improved:

- `improved/agent-workflow.excalidraw`
- `improved/streaming-lifecycle.excalidraw`
- `improved/youtube-pipeline.excalidraw`

Each `.excalidraw` has a rendered `.png` next to it.
