# spec.yaml — full field reference

`spec.yaml` is the single source of truth for a chart. **To change a chart, edit
a field here and re-run `render.py`** — never redraw from scratch.

## Top-level fields

| field | type | applies to | description |
|---|---|---|---|
| `chart_type` | string | all | `bar`, `hbar`, `grouped_bar`, `stacked_bar`, `stacked_bar_100`, `line`, `waterfall`, `slope`, `dumbbell`, `scatter`, `pie`, `donut` |
| `theme` | string | all | `mckinsey` (default), `economist`, `consulting`, `ft` |
| `title` | string | all | The takeaway / action title (bold). |
| `subtitle` | string | all | Context: metric, unit, period (lighter). |
| `data` | map | all | Maps roles → CSV column names (see per-type below). |
| `highlight` | list | bar, hbar, line, slope, pie, donut | Category/series names to render in the accent color; everything else goes gray. |
| `sort` | string | bar, hbar, dumbbell | `desc`, `asc`, or `none`. |
| `value_labels` | bool | bar, hbar, stacked_*, waterfall | Draw value labels on data. Default `true` (bars) / `false` (stacked). |
| `legend` | bool | grouped_bar, stacked_* | Show legend. Default `true`. |
| `number_format` | map | all | `decimals`, `thousands` (bool), `scale` (divide by), `prefix`, `suffix`. |
| `x_label` / `y_label` | string | most | Axis titles. |
| `figsize` | [w, h] | all | Inches. Default `[9, 6]`. |
| `annotations` | list | bar, hbar, line (+ any via `xy`) | Text callouts with a leader line pointing at a data point. See below. |
| `source` | string | all | Shown bottom-left, prefixed automatically as given (write "출처: …"). |
| `note` | string | all | Caveat line, shown as "Note: …" above the source. |
| `output` | map | all | `{ svg: true, png: false }`. `--png` flag also forces PNG. |

## `data` mapping by chart type

| chart_type | required `data` keys | optional |
|---|---|---|
| `bar`, `hbar` | `category`, `value` | — |
| `pie`, `donut` | `category`, `value` | — |
| `grouped_bar` | `category`, `values: [colA, colB, …]` | — |
| `stacked_bar`, `stacked_bar_100` | `category`, `values: [colA, colB, …]` | — |
| `line` | `x` (or `category`), `values: [...]` (or single `value`) | — |
| `waterfall` | `category`, `value` (the +/− deltas) | `total` (column of 0/1 marking absolute bars) |
| `slope` | `category`, `start`, `end` | `start_label`, `end_label` |
| `dumbbell` | `category`, `start`, `end` | `start_label`, `end_label` |
| `scatter` | `x`, `y` | `label` (column to annotate points) |

> Column names are case- and language-sensitive — use exactly what `ingest.py`
> printed. If a numeric column name is a year like `2024`, quote it in YAML:
> `start: "2023"`.

## Examples per type

```yaml
# Ranked horizontal bar with one highlight
chart_type: hbar
theme: economist
title: "북미가 전체 매출 성장을 견인했다"
subtitle: "2024년 지역별 매출 (단위: 백만 USD)"
data: { category: region, value: revenue }
sort: desc
highlight: ["북미"]
number_format: { thousands: true, decimals: 0 }
source: "출처: 사내 ERP, 2024"
```

```yaml
# Waterfall (totals marked by a 0/1 column)
chart_type: waterfall
theme: mckinsey
title: "신규 유입이 순증을 이끌었다"
subtitle: "고객 수 증감 (단위: 천 명)"
data: { category: 단계, value: 값, total: 총계 }
```

```yaml
# Slope: two time points, highlight the mover
chart_type: slope
theme: ft
title: "연구 부서 성과가 급등했다"
subtitle: "2023 → 2024 성과 점수"
data: { category: 부서, start: "2023", end: "2024", start_label: "2023", end_label: "2024" }
highlight: ["연구"]
```

```yaml
# 100% stacked composition
chart_type: stacked_bar_100
theme: consulting
title: "제품 A 비중이 꾸준히 상승했다"
subtitle: "분기별 매출 점유율 (%)"
data: { category: quarter, values: [제품A, 제품B, 제품C] }
value_labels: true
```

## Annotations (text callouts)

Add short notes that point at a specific data point with a leader line. Each
item in the `annotations` list supports:

| field | description |
|---|---|
| `text` | callout text; use `\n` for line breaks |
| `at` | anchor: category name (bar/hbar) or x value (line) |
| `series` | line charts only: which line to anchor to (combine with `at`) |
| `xy` | `[x, y]` explicit data coords — fallback for any chart type |
| `dx`, `dy` | text-box offset from the point, in points (default `36`, `28`) |
| `ha`, `va` | text alignment; inferred from offset sign if omitted |
| `color` | box/arrow color (default = theme accent) |
| `fontsize` | default `10` |

```yaml
annotations:
  # bar/hbar: anchor by category
  - text: "티구안 단독 선두\n2위와 740대 차이"
    at: "티구안"
    dx: -40
    dy: -75
    ha: right
  # line: anchor by series + x value
  - text: "경기 연말 최고치\n2월 대비 +93%"
    series: "경기"
    at: "12월"
    dx: -150
    dy: 18
```
Annotate the *why* (not the value), keep it brief, and tie the color to the
series it refers to. If a box gets clipped at an edge, nudge `dx`/`dy`/`ha`.

## Common edits (recipes)
- Change which item is emphasized → edit `highlight`.
- Switch the look → edit `theme`.
- Reorder bars → edit `sort`.
- Fix the message → edit `title` / `subtitle`.
- Scale units (e.g. show in millions) → `number_format: { scale: 1000000, suffix: "M" }`.
- Add a caveat → set `note:`.

After any edit, re-run:
```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/render.py" --data charts/<name>/data.csv \
  --spec charts/<name>/spec.yaml --out charts/<name>/chart --png
```
