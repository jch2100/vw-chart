#!/usr/bin/env python3
"""Deterministic chart renderer: data.csv + spec.yaml -> SVG (+ optional PNG).

This is the engine behind the data-chart skill. A chart is fully described by a
declarative ``spec.yaml`` plus a normalized ``data.csv``. To MODIFY a chart you
edit fields in the spec and re-run this script — you never redraw from scratch.
That is what makes edits stable instead of destructive.

Usage:
    python3 render.py --data data.csv --spec spec.yaml --out chart.svg [--png]

See ``references/spec-schema.md`` for every supported field, and
``references/chart-types.md`` for choosing a chart type.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import yaml
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

# Local modules (scripts/ is the working dir for imports).
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fonts as _fonts
import themes as _themes


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def fmt_number(value, nf: dict) -> str:
    """Format a number per the spec's number_format block."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    decimals = nf.get("decimals", 0)
    scale = nf.get("scale", 1)
    v = value / scale if scale else value
    if nf.get("thousands", True):
        s = f"{v:,.{decimals}f}"
    else:
        s = f"{v:.{decimals}f}"
    # Strip pointless trailing zeros while keeping integers clean.
    if decimals > 0 and "." in s:
        s = s.rstrip("0").rstrip(".")
    return f"{nf.get('prefix', '')}{s}{nf.get('suffix', '')}"


def bar_colors(categories, theme, highlight):
    """One accent color for highlighted categories, muted gray for the rest.

    When nothing is highlighted, use the theme's primary color throughout.
    """
    if highlight:
        hi = set(highlight)
        return [theme.accent if c in hi else theme.muted for c in categories]
    return [theme.primary] * len(categories)


def resolve(spec_data: dict, df: pd.DataFrame, key: str, default=None):
    """Resolve a column name from the spec's `data` mapping."""
    col = spec_data.get(key, default)
    if col is None:
        return None
    if isinstance(col, list):
        return col
    if col not in df.columns:
        raise SystemExit(f"[render] column '{col}' (data.{key}) not found in CSV. "
                         f"Available: {list(df.columns)}")
    return col


# --------------------------------------------------------------------------- #
# Chart types
# --------------------------------------------------------------------------- #
def _single_series(df, spec, theme):
    """Extract (categories, values) for bar/hbar/pie style charts."""
    d = spec.get("data", {})
    cat = resolve(d, df, "category")
    val = resolve(d, df, "value")
    if cat is None or val is None:
        raise SystemExit("[render] this chart needs data.category and data.value")
    sub = df[[cat, val]].dropna()
    order = spec.get("sort", "none")
    if order == "desc":
        sub = sub.sort_values(val, ascending=False)
    elif order == "asc":
        sub = sub.sort_values(val, ascending=True)
    return sub[cat].astype(str).tolist(), sub[val].tolist()


def chart_bar(ax, df, spec, theme, horizontal=False):
    cats, vals = _single_series(df, spec, theme)
    nf = spec.get("number_format", {})
    colors = bar_colors(cats, theme, spec.get("highlight"))
    if horizontal:
        cats, vals, colors = cats[::-1], vals[::-1], colors[::-1]  # top = first
        ax.barh(cats, vals, color=colors)
        # Anchor each bar at its end (value, row) for annotations.
        ax._anchors = {str(c): (v, i) for i, (c, v) in enumerate(zip(cats, vals))}
        ax.grid(axis="x"); ax.grid(axis="y", visible=False)
        if spec.get("value_labels", True):
            for y, v in enumerate(vals):
                ax.text(v, y, "  " + fmt_number(v, nf), va="center", ha="left",
                        fontsize=10, color=theme.text)
        ax.margins(x=0.12)
    else:
        ax.bar(cats, vals, color=colors)
        ax._anchors = {str(c): (i, v) for i, (c, v) in enumerate(zip(cats, vals))}
        if spec.get("value_labels", True):
            for x, v in enumerate(vals):
                ax.text(x, v, fmt_number(v, nf), va="bottom", ha="center",
                        fontsize=10, color=theme.text)
        ax.margins(y=0.12)
        if max(len(str(c)) for c in cats) > 6:
            plt.setp(ax.get_xticklabels(), rotation=30, ha="right")


def chart_grouped_bar(ax, df, spec, theme):
    d = spec.get("data", {})
    cat = resolve(d, df, "category")
    series = resolve(d, df, "values")
    if not series:
        raise SystemExit("[render] grouped_bar needs data.values: [col1, col2, ...]")
    cats = df[cat].astype(str).tolist()
    n, m = len(cats), len(series)
    width = 0.8 / m
    import numpy as np
    x = np.arange(n)
    nf = spec.get("number_format", {})
    for i, s in enumerate(series):
        ax.bar(x + i * width - 0.4 + width / 2, df[s], width,
               label=s, color=theme.sequence[i % len(theme.sequence)])
    ax.set_xticks(x); ax.set_xticklabels(cats)
    ax.margins(y=0.12)
    _maybe_legend(ax, spec, theme)


def chart_stacked_bar(ax, df, spec, theme, pct=False):
    d = spec.get("data", {})
    cat = resolve(d, df, "category")
    series = resolve(d, df, "values")
    if not series:
        raise SystemExit("[render] stacked_bar needs data.values: [col1, col2, ...]")
    cats = df[cat].astype(str).tolist()
    frame = df[series].astype(float).copy()
    if pct:
        frame = frame.div(frame.sum(axis=1), axis=0) * 100
    bottom = [0.0] * len(cats)
    nf = spec.get("number_format", {})
    for i, s in enumerate(series):
        vals = frame[s].tolist()
        ax.bar(cats, vals, bottom=bottom, label=s,
               color=theme.sequence[i % len(theme.sequence)])
        if spec.get("value_labels", False):
            for x, (b, v) in enumerate(zip(bottom, vals)):
                if v > 0:
                    ax.text(x, b + v / 2, fmt_number(v, nf), ha="center",
                            va="center", fontsize=9, color="white")
        bottom = [b + v for b, v in zip(bottom, vals)]
    if pct:
        ax.set_ylim(0, 100)
    ax.margins(y=0.05)
    _maybe_legend(ax, spec, theme)


def chart_line(ax, df, spec, theme):
    d = spec.get("data", {})
    x = resolve(d, df, "x") or resolve(d, df, "category")
    series = resolve(d, df, "values") or [resolve(d, df, "value")]
    xs = df[x].astype(str).tolist()
    highlight = set(spec.get("highlight") or [])
    anchors = {}
    for s in series:
        ys = df[s].tolist()
        for i, xv in enumerate(xs):
            anchors[f"{s}@{xv}"] = (i, ys[i])
        anchors[str(s)] = (len(xs) - 1, ys[-1])  # series name -> last point
    ax._anchors = anchors
    for i, s in enumerate(series):
        if highlight:
            color = theme.accent if s in highlight else theme.muted
            lw = 2.6 if s in highlight else 1.4
        else:
            color = theme.sequence[i % len(theme.sequence)]
            lw = 2.2
        ax.plot(xs, df[s], color=color, linewidth=lw, marker="o", markersize=4)
        # Direct end-of-line label instead of a legend.
        ax.text(len(xs) - 1, df[s].iloc[-1], "  " + str(s), color=color,
                va="center", ha="left", fontsize=10, fontweight="bold")
    ax.margins(x=0.10, y=0.12)
    if len(xs) > 8:
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")


def chart_waterfall(ax, df, spec, theme):
    d = spec.get("data", {})
    cat = resolve(d, df, "category")
    val = resolve(d, df, "value")
    labels = df[cat].astype(str).tolist()
    deltas = df[val].astype(float).tolist()
    # Optional "is_total" column marks absolute bars (start/end totals).
    totals_col = d.get("total")
    is_total = (df[totals_col].astype(bool).tolist()
                if totals_col and totals_col in df.columns
                else [False] * len(deltas))
    nf = spec.get("number_format", {})
    cum = 0.0
    for i, (lab, dv, tot) in enumerate(zip(labels, deltas, is_total)):
        if tot:
            ax.bar(i, dv, bottom=0, color=theme.primary)
            top = dv
        else:
            base = cum
            color = theme.pos_color if dv >= 0 else theme.neg_color
            ax.bar(i, dv, bottom=base, color=color)
            top = base + dv
            cum = top
        if tot:
            cum = dv
        if spec.get("value_labels", True):
            ax.text(i, top, fmt_number(dv, nf), ha="center",
                    va="bottom" if dv >= 0 else "top", fontsize=9, color=theme.text)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    if max(len(l) for l in labels) > 6:
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    ax.margins(y=0.15)


def chart_slope(ax, df, spec, theme):
    d = spec.get("data", {})
    cat = resolve(d, df, "category")
    start = resolve(d, df, "start")
    end = resolve(d, df, "end")
    nf = spec.get("number_format", {})
    highlight = set(spec.get("highlight") or [])
    left_label = d.get("start_label", start)
    right_label = d.get("end_label", end)
    for _, row in df.iterrows():
        name = str(row[cat])
        y0, y1 = row[start], row[end]
        if highlight:
            color = theme.accent if name in highlight else theme.muted
        else:
            color = theme.primary
        ax.plot([0, 1], [y0, y1], color=color, marker="o", linewidth=2)
        ax.text(-0.03, y0, f"{name}  {fmt_number(y0, nf)}", ha="right",
                va="center", fontsize=9, color=color)
        ax.text(1.03, y1, f"{fmt_number(y1, nf)}  {name}", ha="left",
                va="center", fontsize=9, color=color)
    ax.set_xlim(-0.5, 1.5)
    ax.set_xticks([0, 1]); ax.set_xticklabels([left_label, right_label])
    ax.grid(False)
    ax.spines["left"].set_visible(False)
    ax.set_yticks([])


def chart_dumbbell(ax, df, spec, theme):
    d = spec.get("data", {})
    cat = resolve(d, df, "category")
    start = resolve(d, df, "start")
    end = resolve(d, df, "end")
    nf = spec.get("number_format", {})
    order = spec.get("sort", "none")
    sub = df[[cat, start, end]].copy()
    if order == "desc":
        sub = sub.sort_values(end, ascending=True)
    elif order == "asc":
        sub = sub.sort_values(end, ascending=False)
    cats = sub[cat].astype(str).tolist()
    s_label = d.get("start_label", start)
    e_label = d.get("end_label", end)
    for y, (_, row) in enumerate(sub.iterrows()):
        ax.plot([row[start], row[end]], [y, y], color=theme.muted, linewidth=2, zorder=1)
        ax.scatter(row[start], y, color=theme.muted, s=70, zorder=2)
        ax.scatter(row[end], y, color=theme.accent, s=70, zorder=3)
    ax.set_yticks(range(len(cats))); ax.set_yticklabels(cats)
    ax.grid(axis="x"); ax.grid(axis="y", visible=False)
    ax.margins(x=0.12, y=0.08)
    # Legend mapping the two dots.
    handles = [Line2D([0], [0], marker="o", linestyle="", color=theme.muted, label=str(s_label)),
               Line2D([0], [0], marker="o", linestyle="", color=theme.accent, label=str(e_label))]
    ax.legend(handles=handles, frameon=False, loc="best")


def chart_scatter(ax, df, spec, theme):
    d = spec.get("data", {})
    x = resolve(d, df, "x")
    y = resolve(d, df, "y")
    label = d.get("label")
    ax.scatter(df[x], df[y], color=theme.primary, s=60, alpha=0.85)
    if label and label in df.columns:
        for _, row in df.iterrows():
            ax.text(row[x], row[y], "  " + str(row[label]), fontsize=8,
                    color=theme.subtle_text, va="center")
    ax.set_xlabel(spec.get("x_label", x))
    ax.set_ylabel(spec.get("y_label", y))
    ax.grid(True)


def chart_pie(ax, df, spec, theme, donut=False):
    cats, vals = _single_series(df, spec, theme)
    if len(cats) > 6:
        print(f"[render] WARNING: pie/donut with {len(cats)} slices is hard to read; "
              f"consider a bar chart or grouping small slices into 'Other'.",
              file=sys.stderr)
    hi = set(spec.get("highlight") or [])
    colors = [theme.accent if c in hi else theme.sequence[i % len(theme.sequence)]
              for i, c in enumerate(cats)]
    nf = spec.get("number_format", {})
    wedgeprops = {"width": 0.42} if donut else {}
    ax.pie(vals, labels=cats, colors=colors, startangle=90, counterclock=False,
           autopct=lambda p: fmt_number(p, {**nf, "suffix": "%", "decimals": nf.get("decimals", 0)}),
           wedgeprops=wedgeprops, textprops={"color": theme.text})
    ax.set_aspect("equal")
    ax.grid(False)


DISPATCH = {
    "bar": lambda ax, df, s, t: chart_bar(ax, df, s, t, horizontal=False),
    "hbar": lambda ax, df, s, t: chart_bar(ax, df, s, t, horizontal=True),
    "grouped_bar": chart_grouped_bar,
    "stacked_bar": lambda ax, df, s, t: chart_stacked_bar(ax, df, s, t, pct=False),
    "stacked_bar_100": lambda ax, df, s, t: chart_stacked_bar(ax, df, s, t, pct=True),
    "line": chart_line,
    "waterfall": chart_waterfall,
    "slope": chart_slope,
    "dumbbell": chart_dumbbell,
    "scatter": chart_scatter,
    "pie": lambda ax, df, s, t: chart_pie(ax, df, s, t, donut=False),
    "donut": lambda ax, df, s, t: chart_pie(ax, df, s, t, donut=True),
}


# --------------------------------------------------------------------------- #
# Shared layout / chrome
# --------------------------------------------------------------------------- #
def _maybe_legend(ax, spec, theme):
    if spec.get("legend", True):
        ax.legend(frameon=False, loc="best")


def draw_annotations(ax, spec, theme):
    """Draw text callouts with a leader line pointing at a data point.

    Each item in spec['annotations'] anchors to a data point and places a small
    boxed note offset from it. Anchor a point by `at` (category name, or x value
    for line charts — add `series` to pick the line), or give explicit data
    coordinates with `xy: [x, y]`. Offsets `dx`/`dy` are in points.
    """
    anns = spec.get("annotations") or []
    if not anns:
        return
    anchors = getattr(ax, "_anchors", {})
    for ann in anns:
        text = ann.get("text", "")
        if not text:
            continue
        if "xy" in ann:
            xy = tuple(ann["xy"])
        else:
            if ann.get("series") and ann.get("at") is not None:
                key = f"{ann['series']}@{ann['at']}"
            elif ann.get("at") is not None:
                key = str(ann["at"])
            else:
                key = str(ann.get("series", ""))
            if key not in anchors:
                print(f"[render] WARNING: annotation anchor '{key}' not found; "
                      f"use `xy: [x, y]` or a valid `at`/`series`. Skipping.",
                      file=sys.stderr)
                continue
            xy = anchors[key]
        dx = ann.get("dx", 36)
        dy = ann.get("dy", 28)
        color = ann.get("color", theme.accent)
        ha = ann.get("ha", "left" if dx >= 0 else "right")
        va = ann.get("va", "bottom" if dy >= 0 else "top")
        ax.annotate(
            text, xy=xy, xytext=(dx, dy), textcoords="offset points",
            fontsize=ann.get("fontsize", 10), color=color, fontweight="bold",
            ha=ha, va=va, zorder=10,
            bbox=dict(boxstyle="round,pad=0.45", fc="white", ec=color,
                      lw=1.1, alpha=0.96),
            arrowprops=dict(arrowstyle="->", color=color, lw=1.3,
                            connectionstyle="arc3,rad=0.15"),
        )


def finalize(fig, ax, spec, theme):
    """Add action title, subtitle, source/note, and the Economist tab."""
    left = 0.06
    has_sub = bool(spec.get("subtitle"))
    has_src = bool(spec.get("source") or spec.get("note"))

    top_rule_y = 0.965
    if theme.economist_tab:
        fig.add_artist(Line2D([left, 0.97], [top_rule_y, top_rule_y],
                              color=theme.accent, linewidth=1.4))
        fig.add_artist(Rectangle((left, top_rule_y + 0.004), 0.045, 0.012,
                                 color=theme.accent, transform=fig.transFigure,
                                 clip_on=False))

    title = spec.get("title", "")
    if title:
        fig.text(left, 0.915, title, ha="left", va="top",
                 fontsize=16, fontweight="bold", color=theme.text)
    if has_sub:
        fig.text(left, 0.862, spec["subtitle"], ha="left", va="top",
                 fontsize=11, color=theme.subtle_text)

    if has_src:
        parts = []
        if spec.get("note"):
            parts.append(f"Note: {spec['note']}")
        if spec.get("source"):
            parts.append(spec["source"])
        fig.text(left, 0.02, "\n".join(parts), ha="left", va="bottom",
                 fontsize=8.5, color=theme.subtle_text, alpha=0.85)

    # Reserve room for chrome; widen left margin for horizontal category labels.
    top = 0.80 if has_sub else 0.86
    bottom = 0.16 if has_src else 0.10
    chart_type = spec.get("chart_type")
    left_m = 0.26 if chart_type in ("hbar", "dumbbell") else 0.11
    right_m = 0.80 if chart_type == "slope" else 0.95
    fig.subplots_adjust(left=left_m, right=right_m, top=top, bottom=bottom)


def render(data_path, spec_path, out_path, png=False):
    df = pd.read_csv(data_path)
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f) or {}

    _fonts.register()
    matplotlib.rcParams["svg.fonttype"] = "path"  # embed glyphs -> Korean-safe

    theme = _themes.get(spec.get("theme"))
    _themes.apply(theme)

    chart_type = spec.get("chart_type", "bar")
    if chart_type not in DISPATCH:
        raise SystemExit(f"[render] unknown chart_type '{chart_type}'. "
                         f"Options: {', '.join(DISPATCH)}")

    figsize = spec.get("figsize", [9, 6])
    fig, ax = plt.subplots(figsize=figsize)
    DISPATCH[chart_type](ax, df, spec, theme)
    draw_annotations(ax, spec, theme)

    if spec.get("y_label") and chart_type not in ("scatter", "slope", "pie", "donut"):
        ax.set_ylabel(spec["y_label"])
    if spec.get("x_label") and chart_type not in ("scatter",):
        ax.set_xlabel(spec["x_label"])

    finalize(fig, ax, spec, theme)

    out_path = Path(out_path)
    out_cfg = spec.get("output", {})
    want_svg = out_cfg.get("svg", True)
    want_png = png or out_cfg.get("png", False)

    if want_svg:
        fig.savefig(out_path.with_suffix(".svg"), format="svg")
        print(f"[render] wrote {out_path.with_suffix('.svg')}")
    if want_png:
        fig.savefig(out_path.with_suffix(".png"), format="png", dpi=200)
        print(f"[render] wrote {out_path.with_suffix('.png')}")
    plt.close(fig)


def main():
    p = argparse.ArgumentParser(description="Render a chart from data.csv + spec.yaml")
    p.add_argument("--data", required=True, help="path to normalized data.csv")
    p.add_argument("--spec", required=True, help="path to spec.yaml")
    p.add_argument("--out", required=True, help="output path (extension set by format)")
    p.add_argument("--png", action="store_true", help="also write a PNG preview")
    args = p.parse_args()
    render(args.data, args.spec, args.out, png=args.png)


if __name__ == "__main__":
    main()
