# Style guide — consulting & publication-grade charts

The defaults baked into `render.py` and `themes.py` come from the data-viz
canon: Edward Tufte (*The Visual Display of Quantitative Information*), Cole
Nussbaumer Knaflic (*Storytelling with Data*), Gene Zelazny (*Say It With
Charts*), Stephen Few, and the published house styles of The Economist, the
Financial Times, BBC, McKinsey and BCG. This file explains the *why* so you can
apply judgement, plus the exact palettes with sources.

## 1. Title states the takeaway ("the so what")
The title is the **conclusion**, not the topic. "북미가 전체 매출 성장을 견인했다"
beats "지역별 매출". One chart = one message. The subtitle carries context:
what is measured, in what unit, over what period. Bold, left-aligned title;
lighter, left-aligned subtitle — the FT/Economist/BBC convention (BBC's
`finalise_plot()` left-aligns both).

## 2. One accent color; gray everything else
Color is a tool to **direct attention**, not decoration. Pre-attentive
attributes (color, weight, size) let the eye find the point without conscious
effort. So: mute all context to gray and use a **single accent** for the data
that carries the message. The Economist applies this at brand level — red
(`#E3120B`) is *rationed* for emphasis, never sprayed across all series. In this
skill, `highlight:` drives exactly this behavior.

## 3. Declutter — maximize the data-ink ratio (Tufte)
Every element must earn its place. The themes remove top/right spines, drop tick
marks, use faint gridlines on one axis only, and avoid 3D, heavy borders, and
backgrounds-for-their-own-sake. If it doesn't help the reader see the insight,
it's removed.

## 4. Label directly; avoid legends
Legends force the eye back and forth, adding cognitive load. Label data in place:
bars get value labels, line series get their name at the endpoint. Label **only
what matters** (endpoints, the peak, the focal series) — not every point.

## 5. Annotate the "why," not the "what"
Use callouts to explain a spike, an outlier, or why a number matters — don't
restate the value. Tie a note to its data by proximity, a thin leader line, or
by coloring the annotation to match the series. Annotations carry the
interpretation so the audience doesn't have to do analysis live.

## 6. Number formatting
Round aggressively — extra decimals imply false precision. Strip trailing zeros
("1.5" not "1.500"). Use thousands separators (`123,456`) or abbreviate
(`123.5M`) and put the multiplier/unit in the **subtitle or axis title**, not on
every tick. Use clean tick intervals (0, 50, 100…). Configure via
`number_format` (`decimals`, `thousands`, `scale`, `prefix`, `suffix`).

## 7. Layout order (top → bottom)
1. (Economist look) red top rule + small red corner tab
2. **Title** — bold, left-aligned, the takeaway
3. **Subtitle** — lighter, left-aligned, unit + period
4. the chart, with direct labels/annotations
5. **`Source:`** line, small, bottom-left (~75% opacity); **`Note:`** for caveats

---

## Palettes (encoded sources)

Each theme defines: `primary` (default data color), `accent` (the one highlight),
`muted` (context/gray), a `sequence` for multi-series, and backgrounds.

### The Economist — `theme: economist` (default)
Blues / grays / greens; **red rationed for emphasis**; bluish-gray panel.
- primary `#014d64` · accent `#E3120B` (Economist Red) · muted `#adadad`
- panel/background `#d5e4eb` · sequence: `#014d64, #6794a7, #01a2d9, #76c0c1, #00887d, #a18376`
- Source: [highcharter `theme-economist.R`](https://github.com/jbkunst/highcharter/blob/main/R/theme-economist.R), [`ggthemes::economist_pal()`](https://jrnold.github.io/ggthemes/reference/economist_pal.html); red [shadcn.io Economist](https://www.shadcn.io/design/economist).

### McKinsey — `theme: mckinsey`
"Deep blue against white" with a bright electric-blue accent.
- primary `#051C2C` (Black Pearl) · accent `#2251FF` (Blue Ribbon) · muted ≈ `#C0C5C9`
- white canvas · cyan `#00A9F4` (approximate)
- Source: [Brandfetch – mckinsey.com](https://brandfetch.com/mckinsey.com), [Slideworks – McKinsey identity](https://slideworks.io/resources/decoding-mckinseys-visual-identity-and-powerpoint-template), [Datawrapper style-guide notes](https://www.datawrapper.de/blog/colors-for-data-vis-style-guides). (McKinsey publishes no open palette package; cyan/gray are approximate.)

### BCG / consulting — `theme: consulting`
Distinctive green (vs competitors' navy); magenta/yellow accents.
- primary `#2ABA75` (BCG green) · accent `#E71B56` (magenta) · muted `#9A9A9A` (`#7F7F7F` axis)
- background `#F2F2F2`/white · sequence includes `#295E7E, #1A7A55, #DEE341`
- Source: [`bcggtheme` palette](https://rdrr.io/github/Tony-Chen-Melbourne/bcggtheme/man/bcg_green_1.html) (hard-coded in the package).

### Financial Times — `theme: ft`
Signature salmon "paper" background.
- primary `#0F5499` (Oxford blue) · accent `#990F3D` (Claret) · muted/dark `#262A33` (Slate)
- background `#FFF1E5` (Paper) · also teal `#0D7680`, mandarin `#FF8833`
- Source: [Financial-Times/o-colors](https://github.com/Financial-Times/o-colors), [`ftplottools::ft_colors`](https://rdrr.io/github/Financial-Times/ftplottools/man/ft_colors.html).

| Firm | Primary | Accent / highlight | Muted / background |
|---|---|---|---|
| Economist | `#014d64` | `#E3120B` | `#adadad` / `#d5e4eb` |
| McKinsey | `#051C2C` | `#2251FF` | `#C0C5C9` / white |
| BCG (consulting) | `#2ABA75` | `#E71B56` | `#7F7F7F` / `#F2F2F2` |
| FT | `#0F5499` | `#990F3D` | `#262A33` / `#FFF1E5` |

---

## Pre-flight checklist
- [ ] Title is the takeaway; subtitle has unit + period.
- [ ] One accent color via `highlight:`; rest is gray.
- [ ] Data labeled directly; only key points labeled.
- [ ] Numbers rounded, thousands separated; unit in subtitle/axis.
- [ ] `source:` set; `note:` for caveats.
- [ ] Verified the rendered PNG (Korean OK, no overlapping labels).

**Anchor references:** [FT Visual Vocabulary](https://github.com/Financial-Times/chart-doctor) ·
[BBC R Cookbook / bbplot](https://bbc.github.io/rcookbook/) ·
*Storytelling with Data*, Ch. 4 (pre-attentive attributes) ·
Tufte, *The Visual Display of Quantitative Information* ·
[EU data-visualisation guide](https://data.europa.eu/apps/data-visualisation-guide/).
