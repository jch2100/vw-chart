# Chart-type selection — the FT "Visual Vocabulary"

Choose a chart by the **relationship you need to communicate**, not by habit.
This is the framework used by the Financial Times Visual Journalism team
(chart-doctor repo) and echoed in Gene Zelazny's *Say It With Charts* and the
EU data-visualisation guide. Below: the nine message categories, the chart types
that fit, and which of those this skill renders (`chart_type` values in **bold**).

| Category | The message | Recommended charts (✅ = supported here) |
|---|---|---|
| **Magnitude** | size comparison of counted values | ✅ **bar**, ✅ **hbar**, ✅ **grouped_bar**, paired bar, lollipop |
| **Ranking** | position in an ordered list matters | ✅ **hbar** (sorted), ✅ **dumbbell**, ✅ **slope**, dot strip, lollipop |
| **Change over time** | trend over a period | ✅ **line**, column, ✅ **slope**, area, fan chart |
| **Part-to-whole** | one entity split into components | ✅ **stacked_bar**, ✅ **stacked_bar_100**, ✅ **pie**/**donut**, ✅ **waterfall**, treemap, marimekko |
| **Deviation** | +/− from a reference point | ✅ **waterfall**, diverging bar, surplus/deficit line |
| **Correlation** | relationship between variables | ✅ **scatter**, bubble, connected scatter, XY heatmap |
| **Distribution** | values and how often they occur | histogram, boxplot, violin, population pyramid |
| **Flow** | movement between states | Sankey, ✅ **waterfall**, chord, network |
| **Spatial** | location/geography is the point | choropleth, proportional-symbol map, cartogram |

> Distribution and Spatial charts are out of scope for v1 — use a bar/scatter
> approximation, or note the limitation.

---

## When to use each supported type

### `bar` (vertical columns)
Few categories (≤ ~8), short labels. Comparing magnitudes. For time, columns
read left→right naturally. Sort by value unless a natural order exists.

### `hbar` (horizontal bars) — the consultant's default
Use when **labels are long** (no rotated text), when you are **ranking**
(sort `desc`, biggest on top — matches how we scan a list), or with many
categories (10–20). Do **not** use for time series.

### `grouped_bar`
A few categories × a few series (≤ ~4 series). Compares series within each
category. Beyond that it gets noisy — prefer small multiples (not yet supported)
or separate charts.

### `stacked_bar` vs `stacked_bar_100`
- `stacked_bar`: part-to-whole **and the total matters** (absolute values).
- `stacked_bar_100`: **composition/share** matters and you want unequal totals
  comparable on share alone.
- Caveat: only the bottom segment and the total are easy to read accurately.
  Keep ≤ ~4 segments; put the most important series at the base.

### `line`
Trends over time, especially many points. Highlight the one series that carries
the story (`highlight:`); others go gray. Series are labeled at their endpoints
(no legend needed). Avoid "spaghetti" — if > ~5 series compete, highlight one.

### `waterfall` (bridge) — a McKinsey signature
Explains **how you get from one total to another** via sequential +/−
contributions (revenue→profit drivers, period-over-period bridge, gap to
target). Mark the absolute start/end bars with a `total` column = 1. Increases
and decreases get distinct colors automatically.

### `slope`
Exactly **two** time points/conditions; the story is direction + magnitude of
change (and rank swaps). Breaks down beyond ~15 lines. Highlight the mover.

### `dumbbell` (connected dot)
**Two values per category**, emphasizing the **gap** (before/after, 2023 vs
2024, actual vs target). A cleaner alternative to paired bars. Use `slope` when
direction matters more than the size of the gap.

### `scatter`
Relationship between two numeric variables. Add a `label` column to annotate
points. Keep it to a readable number of points.

### `pie` / `donut` — use sparingly
Only for a **single** part-to-whole snapshot with a clear dominant slice.
**Max ~5 slices** (group the rest into "기타/Other"). Never use multiple pies to
show change over time — use `stacked_bar_100` or `slope` instead. The renderer
warns above 6 slices.

---

## Quick decision flow
1. Time on an axis? → `line` (many points) or `slope` (two points).
2. Getting from total A to total B? → `waterfall`.
3. Ranking items / long labels? → `hbar` sorted.
4. Gap between two values per item? → `dumbbell`.
5. Composition? → `stacked_bar_100` (share) / `stacked_bar` (totals); `pie` only if ≤5 and one snapshot.
6. Two numeric variables? → `scatter`.
7. Otherwise comparing magnitudes? → `bar` / `grouped_bar`.

**Sources:** [FT chart-doctor Visual Vocabulary](https://github.com/Financial-Times/chart-doctor/blob/main/visual-vocabulary/README.md) ·
[EU data-visualisation guide](https://data.europa.eu/apps/data-visualisation-guide/visual-vocabulary) ·
Gene Zelazny, *Say It With Charts* · Stephen Few, *Perceptual Edge*.
