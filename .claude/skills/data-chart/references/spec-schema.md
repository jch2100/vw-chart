# spec.yaml — full field reference

`spec.yaml` is the single source of truth for a chart. **To change a chart, edit
a field here and re-run `render.py`** — never redraw from scratch.

## Top-level fields

| field | type | applies to | description |
|---|---|---|---|
| `chart_type` | string | all | `bar`, `hbar`, `grouped_bar`, `stacked_bar`, `stacked_bar_100`, `line`, `waterfall`, `slope`, `dumbbell`, `scatter`, `pie`, `donut` |
| `theme` | string | all | `economist` (default), `mckinsey`, `consulting`, `ft` |
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
