---
name: data-chart
description: >-
  Turn pasted CSV / XLSX / Excel data into polished, consulting-grade charts
  (McKinsey / Economist / BCG style) as SVG. Use whenever the user pastes
  tabular data or a spreadsheet and wants to visualize it, or asks for a chart,
  graph, plot, bar/line/pie/waterfall, 차트, 시각화, 그래프, or to edit an
  existing chart. Korean text is fully supported.
when_to_use: >-
  visualize this data, make a chart, plot this, 차트 만들어줘, 그래프로 보여줘,
  이 데이터 시각화, chart this CSV, graph this Excel, edit/modify the chart,
  change the color/title/highlight, 차트 수정해줘
allowed-tools: Bash(python3 *), Read, Edit, Write
---

# data-chart — editable, consulting-grade charts from data

A chart here is **three files**, not a one-off image:

| file | role | who edits it |
|------|------|--------------|
| `data.csv`  | the normalized data | rarely (only if data changes) |
| `spec.yaml` | every visual decision (type, title, colors, highlight, source…) | **this is what you edit to change the chart** |
| `chart.svg` | rendered output | never by hand — regenerate it |

> ## ⛔ THE ONE RULE — how to MODIFY a chart
> When the user asks for ANY change ("make the bar red", "highlight Europe",
> "change the title", "sort descending", "use the McKinsey theme"):
> **`Edit` the relevant field(s) in `spec.yaml`, then re-run `render.py`.**
> NEVER rewrite the chart from scratch, never hand-edit the SVG, never start a
> new spec. Editing one field and re-rendering is what keeps modifications
> stable instead of degrading the chart. This is the whole point of the skill.

Work inside a per-chart folder, e.g. `charts/<name>/` holding `data.csv`,
`spec.yaml`, `chart.svg`.

---

## Workflow

### 1. Ingest the data
Save the user's pasted data or spreadsheet, then normalize it:

```bash
# from a pasted block saved to raw.csv, or directly from .xlsx:
python3 "${CLAUDE_SKILL_DIR}/scripts/ingest.py" --in raw.xlsx --out charts/<name>/data.csv
# or pipe a pasted CSV/TSV on stdin:
cat raw.txt | python3 "${CLAUDE_SKILL_DIR}/scripts/ingest.py" --out charts/<name>/data.csv
```
It prints the cleaned column names — use those exact names in the spec.

### 2. Choose the chart type from the MESSAGE
Pick the type from what the user wants to *say*, not by habit. Quick guide
(full version in [references/chart-types.md](references/chart-types.md)):

| The message is about… | Use |
|---|---|
| Ranking / comparing items (esp. long labels) | `hbar` (sorted) |
| Comparing values across few categories | `bar` |
| A few groups × a few series | `grouped_bar` |
| Composition / share within categories | `stacked_bar`, `stacked_bar_100` |
| Trend over time | `line` |
| How a total changes via +/− drivers | `waterfall` |
| Change between exactly two points in time | `slope` |
| The gap between two values per item | `dumbbell` |
| Relationship between two variables | `scatter` |
| One part-to-whole snapshot, ≤5 slices | `pie`, `donut` |

### 3. Write `spec.yaml` (apply the design defaults below) and render
```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/render.py" \
  --data charts/<name>/data.csv --spec charts/<name>/spec.yaml \
  --out charts/<name>/chart --png
```
Then **Read the resulting PNG** to verify it looks right (Korean OK, highlight
correct, labels not overlapping) before showing the user. Deliver the `.svg`.

### 4. Modify on request → see THE ONE RULE above.

---

## Design defaults (these make it look like a consulting deck)

Apply these unless the user says otherwise. Rationale + sources in
[references/style-guide.md](references/style-guide.md).

- **Title = the takeaway (action title)**, not the topic. Write the conclusion:
  "북미가 전체 매출 성장을 견인했다" — not "지역별 매출". Put the metric, unit,
  and period in the `subtitle`.
- **One accent, everything else gray.** Set `highlight:` to the one item/series
  that carries the message; the rest renders muted automatically.
- **Direct labels over legends.** `value_labels: true` for bars; line series are
  labeled at their endpoints automatically.
- **Round numbers**, add thousands separators, put the unit in the subtitle —
  configure via `number_format`.
- **Always add a `source:`** line; use `note:` for caveats.
- **Default theme is `economist`.** Other themes: `consulting` (BCG green),
  `mckinsey` (deep + electric blue), `ft` (salmon paper). Match the audience.

## spec.yaml — minimal example
```yaml
chart_type: hbar
theme: economist
title: "북미가 전체 매출 성장을 견인했다"
subtitle: "2024년 지역별 매출 (단위: 백만 USD)"
data: { category: region, value: revenue }
sort: desc
highlight: ["북미"]
value_labels: true
number_format: { thousands: true, decimals: 0 }
source: "출처: 사내 ERP, 2024"
output: { svg: true, png: true }
```
Every field, for every chart type, is documented in
[references/spec-schema.md](references/spec-schema.md). A working example lives in
`examples/` (`sales.csv` + `sales.spec.yaml` → `sales.svg`).

## Notes
- Korean is guaranteed: the renderer bundles NanumGothic and embeds glyphs as
  vector paths (`svg.fonttype=path`), so SVGs show Korean anywhere.
- Requires `pandas matplotlib pyyaml openpyxl`. If a render fails on import,
  run `pip install pandas matplotlib pyyaml openpyxl` once.
- SVG inserts cleanly into PowerPoint (Microsoft 365). Use `--png` for a quick
  preview or for older Office.
