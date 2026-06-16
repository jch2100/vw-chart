"""Chart themes — consulting / publication-grade palettes and styling.

Palettes are taken from authoritative, encoded sources (ggthemes/highcharter
Economist theme, bcggtheme, McKinsey brand, FT o-colors). Each theme defines a
muted context color, one accent/highlight color, an ordered color sequence for
multi-series charts, backgrounds, and matplotlib rcParams. See
``references/style-guide.md`` for sources and rationale.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List
import matplotlib


@dataclass(frozen=True)
class Theme:
    name: str
    primary: str          # default color for single-series data
    accent: str           # highlight color (one, used sparingly)
    muted: str            # context / de-emphasized series
    sequence: List[str]   # ordered colors for multi-series
    figure_bg: str        # area outside the plot
    panel_bg: str         # plot area
    grid: str             # gridline color
    text: str             # main text color
    subtle_text: str      # subtitle / source color
    economist_tab: bool = False  # red top rule + corner tab (Economist look)
    pos_color: str = ""   # waterfall increases
    neg_color: str = ""   # waterfall decreases

    def __post_init__(self):
        # Sensible defaults for waterfall up/down if not set.
        if not self.pos_color:
            object.__setattr__(self, "pos_color", self.primary)
        if not self.neg_color:
            object.__setattr__(self, "neg_color", self.accent)


THEMES = {
    # The Economist — blues/grays/greens, red rationed for emphasis.
    "economist": Theme(
        name="economist",
        primary="#014d64",
        accent="#E3120B",
        muted="#adadad",
        sequence=["#014d64", "#6794a7", "#01a2d9", "#76c0c1", "#00887d", "#a18376"],
        figure_bg="#d5e4eb",
        panel_bg="#d5e4eb",
        grid="#b7cdd9",
        text="#1a1a1a",
        subtle_text="#5c5c5c",
        economist_tab=True,
        pos_color="#014d64",
        neg_color="#E3120B",
    ),
    # Consulting / BCG — green primary, magenta/yellow accents.
    "consulting": Theme(
        name="consulting",
        primary="#2ABA75",
        accent="#E71B56",
        muted="#9A9A9A",
        sequence=["#2ABA75", "#295E7E", "#1A7A55", "#DEE341", "#3EAD92", "#741E92"],
        figure_bg="#FFFFFF",
        panel_bg="#FFFFFF",
        grid="#E2E2E2",
        text="#262626",
        subtle_text="#6E6F73",
        pos_color="#2ABA75",
        neg_color="#E71B56",
    ),
    # McKinsey — deep blue base, electric-blue accent, white canvas.
    "mckinsey": Theme(
        name="mckinsey",
        primary="#051C2C",
        accent="#2251FF",
        muted="#C0C5C9",
        sequence=["#051C2C", "#2251FF", "#00A9F4", "#034B6F", "#6E8898", "#9DB4C0"],
        figure_bg="#FFFFFF",
        panel_bg="#FFFFFF",
        grid="#E6E8EA",
        text="#051C2C",
        subtle_text="#6E7B85",
        pos_color="#2251FF",
        neg_color="#051C2C",
    ),
    # Financial Times — Oxford blue, claret, salmon "paper" background.
    "ft": Theme(
        name="ft",
        primary="#0F5499",
        accent="#990F3D",
        muted="#B3A9A0",
        sequence=["#0F5499", "#990F3D", "#0D7680", "#FF8833", "#262A33", "#9E2F50"],
        figure_bg="#FFF1E5",
        panel_bg="#FFF1E5",
        grid="#E6D9CC",
        text="#33302E",
        subtle_text="#66605C",
        pos_color="#0F5499",
        neg_color="#990F3D",
    ),
}

DEFAULT_THEME = "mckinsey"


def get(name: str | None) -> Theme:
    """Return a Theme by name, falling back to the default."""
    return THEMES.get((name or DEFAULT_THEME).lower(), THEMES[DEFAULT_THEME])


def apply(theme: Theme) -> None:
    """Apply a theme to matplotlib rcParams (declutter + house style)."""
    rc = matplotlib.rcParams
    rc["figure.facecolor"] = theme.figure_bg
    rc["axes.facecolor"] = theme.panel_bg
    rc["savefig.facecolor"] = theme.figure_bg
    rc["text.color"] = theme.text
    rc["axes.labelcolor"] = theme.text
    rc["axes.edgecolor"] = theme.subtle_text
    rc["xtick.color"] = theme.subtle_text
    rc["ytick.color"] = theme.subtle_text
    rc["axes.titlecolor"] = theme.text
    # Declutter: no top/right spines, light grid, no chartjunk.
    rc["axes.spines.top"] = False
    rc["axes.spines.right"] = False
    rc["axes.grid"] = True
    rc["axes.grid.axis"] = "y"
    rc["grid.color"] = theme.grid
    rc["grid.linewidth"] = 0.8
    rc["axes.axisbelow"] = True
    rc["xtick.major.size"] = 0
    rc["ytick.major.size"] = 0
    rc["font.size"] = 11
