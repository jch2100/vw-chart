"""Korean-safe font registration for matplotlib.

Registers the bundled NanumGothic fonts (and any system CJK fonts found) so
that Korean text renders correctly. Combined with ``svg.fonttype = 'path'``
in render.py, glyphs are embedded as vector paths, guaranteeing that Korean
shows up even in viewers without the font installed (no more tofu boxes).
"""
from __future__ import annotations

import os
import matplotlib
from matplotlib import font_manager

# scripts/ -> skill root -> assets/fonts
_SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_FONT_DIR = os.path.join(_SKILL_ROOT, "assets", "fonts")

# Common locations for a Korean-capable system font, used as a fallback.
_SYSTEM_FONT_HINTS = (
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",  # macOS
    "C:/Windows/Fonts/malgun.ttf",                 # Windows
)

_PREFERRED_FAMILY = "NanumGothic"
_registered = False


def register() -> str:
    """Register bundled + system Korean fonts and set the default family.

    Returns the font family name matplotlib will use for Korean text.
    Idempotent: safe to call more than once.
    """
    global _registered

    # Register the bundled fonts first so they win regardless of the system.
    if os.path.isdir(_FONT_DIR):
        for name in os.listdir(_FONT_DIR):
            if name.lower().endswith((".ttf", ".otf")):
                try:
                    font_manager.fontManager.addfont(os.path.join(_FONT_DIR, name))
                except Exception:
                    pass

    # Register any system Korean fonts we can find, as a secondary source.
    for path in _SYSTEM_FONT_HINTS:
        if os.path.exists(path):
            try:
                font_manager.fontManager.addfont(path)
            except Exception:
                pass

    available = {f.name for f in font_manager.fontManager.ttflist}
    if _PREFERRED_FAMILY in available:
        family = _PREFERRED_FAMILY
    else:
        # Fall back to any registered CJK-capable family, else matplotlib default.
        family = next(
            (n for n in available if any(k in n for k in ("Noto Sans CJK", "Malgun", "Apple SD Gothic", "Nanum"))),
            matplotlib.rcParams["font.family"][0]
            if matplotlib.rcParams["font.family"] else "sans-serif",
        )

    matplotlib.rcParams["font.family"] = family
    # Keep the minus sign as ASCII so it never renders as a missing glyph.
    matplotlib.rcParams["axes.unicode_minus"] = False
    _registered = True
    return family


if __name__ == "__main__":
    print("Registered font family:", register())
