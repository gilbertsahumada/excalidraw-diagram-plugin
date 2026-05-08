# Color Palette & Brand Style

**This is the single source of truth for all colors and brand-specific styles.** To customize diagrams for your own brand, edit this file — everything else in the skill is universal.

---

## Shape Colors (Semantic)

Colors encode meaning, not decoration. Each semantic purpose has a fill/stroke pair.

| Semantic Purpose | Fill | Stroke |
|------------------|------|--------|
| Primary/Neutral | `#3b82f6` | `#1e3a5f` |
| Secondary | `#60a5fa` | `#1e3a5f` |
| Tertiary | `#93c5fd` | `#1e3a5f` |
| Start/Trigger | `#fed7aa` | `#c2410c` |
| End/Success | `#a7f3d0` | `#047857` |
| Warning/Reset | `#fee2e2` | `#dc2626` |
| Decision | `#fef3c7` | `#b45309` |
| AI/LLM | `#ddd6fe` | `#6d28d9` |
| Inactive/Disabled | `#dbeafe` | `#1e40af` (use dashed stroke) |
| Error | `#fecaca` | `#b91c1c` |

**Rule**: Always pair a darker stroke with a lighter fill for contrast.

---

## Text Colors (Hierarchy)

Use color on free-floating text to create visual hierarchy without containers.

| Level | Color | Use For |
|-------|-------|---------|
| Title | `#1e40af` | Section headings, major labels |
| Subtitle | `#3b82f6` | Subheadings, secondary labels |
| Body/Detail | `#64748b` | Descriptions, annotations, metadata |
| On light fills | `#374151` | Text inside light-colored shapes |
| On dark fills | `#ffffff` | Text inside dark-colored shapes |

---

## Evidence Artifact Colors

Used for code snippets, data examples, and other concrete evidence inside technical diagrams.

| Artifact | Background | Text Color |
|----------|-----------|------------|
| Code snippet | `#1e293b` | Syntax-colored (language-appropriate) |
| JSON/data example | `#1e293b` | `#22c55e` (green) |

---

## Default Stroke & Line Colors

| Element | Color |
|---------|-------|
| Arrows | Use the stroke color of the source element's semantic purpose |
| Structural lines (dividers, trees, timelines) | Primary stroke (`#1e3a5f`) or Slate (`#64748b`) |
| Marker dots (fill + stroke) | Primary fill (`#3b82f6`) |

---

## Fill Styles

Excalidraw supports three fill patterns inside shapes. Use them to add visual texture and distinguish element types.

| fillStyle | Visual | When to use |
|-----------|--------|-------------|
| `solid` | Flat color fill | Default — clean, modern. Use for most shapes |
| `hachure` | Diagonal line hatching | Highlight "in-progress" or "draft" elements. Adds hand-drawn feel |
| `cross-hatch` | Cross-hatched grid pattern | Emphasize important shapes. Creates visual weight. Good for hero elements |

**Pair with `roughness: 1`** for a hand-drawn aesthetic, or `roughness: 0` for clean hatching.

Use fill styles to create **visual hierarchy**: hero shapes get `cross-hatch`, supporting shapes get `hachure`, background shapes get `solid`. Don't use the same fill style for all shapes in a diagram.

---

## Stroke & Arrow Styles

| strokeStyle | Visual | When to use |
|-------------|--------|-------------|
| `solid` | Continuous line ———— | Default connections, primary flow |
| `dashed` | Dashed line - - - - | Optional paths, async flow, feedback loops, "maybe" connections |
| `dotted` | Dotted line ······· | Weak relationships, annotations, secondary detail |

**Arrow heads** (`endArrowhead` / `startArrowhead`):

| Value | Visual | When to use |
|-------|--------|-------------|
| `"arrow"` | ➤ filled triangle | Default — shows direction |
| `"bar"` | ⊢ flat bar | Shows termination / boundary |
| `"dot"` | ● circle | Shows connection point / endpoint |
| `"triangle"` | △ open triangle | Lighter directional hint |
| `null` | no head | Structural lines, not directional |

Mix stroke styles in one diagram: primary flow = solid, feedback = dashed, annotations = dotted. This creates visual depth.

---

## Background

| Mode | Canvas | When to use |
|------|--------|-------------|
| Light (default) | `#ffffff` | Print, docs, presentations on light backgrounds |
| Dark | `#0f172a` (slate-900) | Most native users prefer dark — match their canvas |

---

## Dark Mode Palette

When `appState.viewBackgroundColor` is dark, swap to these. Default colors look washed out on dark canvas.

### Shape colors (dark)

| Semantic Purpose | Fill | Stroke |
|------------------|------|--------|
| Primary/Neutral | `#1e3a8a` | `#60a5fa` |
| Secondary | `#1e40af` | `#93c5fd` |
| Tertiary | `#312e81` | `#a5b4fc` |
| Start/Trigger | `#7c2d12` | `#fb923c` |
| End/Success | `#064e3b` | `#34d399` |
| Warning/Reset | `#7f1d1d` | `#f87171` |
| Decision | `#78350f` | `#fbbf24` |
| AI/LLM | `#4c1d95` | `#c4b5fd` |
| Inactive/Disabled | `#1e293b` | `#475569` (dashed) |
| Error | `#7f1d1d` | `#fca5a5` |

**Inverted rule**: dark fill + bright stroke (opposite of light mode). Stroke "lights up" the shape against dark canvas.

### Text colors (dark)

| Level | Color | Use |
|-------|-------|-----|
| Title | `#f1f5f9` (slate-100) | Section headings |
| Subtitle | `#cbd5e1` (slate-300) | Secondary labels |
| Body/Detail | `#94a3b8` (slate-400) | Annotations |
| On dark fills | `#f8fafc` | Text inside shapes |

### Evidence artifacts (dark)

Code blocks already use `#1e293b` background — works in BOTH modes. Bump text contrast slightly:

| Mode | Background | Text |
|------|-----------|------|
| Light evidence | `#1e293b` | `#22c55e` |
| Dark evidence | `#020617` (deeper) | `#4ade80` (brighter green) |

### Default lines (dark)

| Element | Color |
|---------|-------|
| Arrows | Use stroke from semantic palette above |
| Structural lines | `#475569` or `#94a3b8` |
| Marker dots | `#60a5fa` |
