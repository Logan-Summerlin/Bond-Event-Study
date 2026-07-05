"""Shared plotting: minimal style, numbered event markers, probability bands.

Design rules: recessive hairline grid, thin marks, a fixed categorical
palette (CVD-validated ordering - do not reorder or cycle), no chartjunk.
Event chronologies are drawn as numbered vertical hairlines whose key is
placed in a footnote under the figure, instead of text stacked inside the
plotting area.
"""

from __future__ import annotations

import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

# fixed categorical order (validated: worst adjacent CVD dE >= 21)
PALETTE = ["#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7", "#e34948"]
UNION_BLUE, CSA_RED = "#2a78d6", "#e34948"

SURFACE = "#fcfcfb"
INK = "#0b0b0b"          # primary text
INK2 = "#52514e"         # secondary text
MUTED = "#898781"        # axis ticks / event badges
HAIRLINE = "#e1e0d9"     # gridlines
BASELINE = "#c3c2b7"     # axis line, event markers

plt.rcParams.update({
    "figure.figsize": (11, 6),
    "figure.dpi": 150,
    "figure.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "grid.color": HAIRLINE,
    "grid.linewidth": 0.8,
    "grid.linestyle": "-",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": False,
    "axes.edgecolor": BASELINE,
    "axes.linewidth": 0.8,
    "axes.titlelocation": "left",
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.titlecolor": INK,
    "axes.titlepad": 14,
    "axes.labelcolor": INK2,
    "axes.labelsize": 9.5,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "text.color": INK,
    "lines.linewidth": 2.0,
    "lines.solid_capstyle": "round",
    "lines.solid_joinstyle": "round",
    "legend.frameon": False,
    "legend.fontsize": 9,
    "font.size": 10,
    "font.family": "sans-serif",
})


def select_events(events: pd.DataFrame, names: list[str] | None = None,
                  max_events: int = 12) -> pd.DataFrame:
    """Curate a chronology down to the events worth marking on a figure.

    `names` is a list of substrings (case-insensitive) matched against the
    event text; without it, major events are kept up to `max_events`.
    """
    ev = events.dropna(subset=["date"]).sort_values("date")
    if names:
        pat = "|".join(names)
        ev = ev[ev["event"].str.contains(pat, case=False)]
    elif "major" in ev.columns:
        ev = ev[ev["major"] == 1]
    return ev.head(max_events).reset_index(drop=True)


def mark_events(ax, events: pd.DataFrame, numbered: bool = True):
    """Vertical hairlines at event dates; small numbered badges on top.

    The badge numbers are keyed by `event_key`, which the caller places
    under the figure via `save_fig(..., footnote=...)`.
    """
    trans = ax.get_xaxis_transform()
    for i, (_, row) in enumerate(events.iterrows()):
        ax.axvline(row["date"], color=BASELINE, lw=0.8, zorder=1)
        if numbered:
            x = matplotlib.dates.date2num(row["date"])
            ax.annotate(str(i + 1), xy=(x, 1.0), xycoords=trans,
                        xytext=(0, 5 + 11 * (i % 2)), textcoords="offset points",
                        ha="center", va="bottom", fontsize=7, color=INK2,
                        bbox=dict(boxstyle="circle,pad=0.22", fc=SURFACE,
                                  ec=BASELINE, lw=0.8),
                        annotation_clip=False)
    return ax


def event_key(events: pd.DataFrame, width: int = 125) -> str:
    """Footnote text keying badge numbers to event names and dates.

    Entries are kept whole - lines break between entries, never inside one.
    """
    parts = [f"{i + 1}  {row['event']} ({row['date'].strftime('%b %Y')})"
             for i, (_, row) in enumerate(events.iterrows())]
    lines, cur = [], ""
    for p in parts:
        cand = f"{cur}      {p}" if cur else p
        if cur and len(cand) > width:
            lines.append(cur)
            cur = p
        else:
            cur = cand
    if cur:
        lines.append(cur)
    return "\n".join(lines)


def annotated_series(ax, series_map: dict[str, pd.Series],
                     events: pd.DataFrame | None = None,
                     ylabel: str = "", title: str = "",
                     colors: dict[str, str] | None = None,
                     numbered: bool = True):
    """One or more price series with numbered event markers."""
    for i, (label, s) in enumerate(series_map.items()):
        c = (colors or {}).get(label, PALETTE[i % len(PALETTE)])
        ax.plot(s.index, s.values, color=c, label=label, zorder=3)
    has_badges = events is not None and len(events) and numbered
    if events is not None and len(events):
        mark_events(ax, events, numbered=numbered)
    ax.set_ylabel(ylabel)
    # the badge row sits above the axes, so push the title clear of it
    ax.set_title(title, pad=36 if has_badges else None)
    year_ticks(ax)
    if len(series_map) > 1:
        ax.legend(loc="best")
    ax.margins(x=0.01)
    return ax


def year_ticks(ax, step: int | None = None):
    """Clean year-only ticks for multi-year monthly series.

    Without `step`, picks 1/2/5/10-year spacing so long spans (the
    60-year Ottoman panel) don't collide.
    """
    if step is None:
        lo, hi = ax.get_xlim()
        span = (hi - lo) / 365.25
        step = next((s for s in (1, 2, 5, 10) if span / s <= 15), 10)
    ax.xaxis.set_major_locator(matplotlib.dates.YearLocator(base=step))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%Y"))
    return ax


def prob_band(ax, bands: pd.DataFrame, central: str, label: str,
              color: str = PALETTE[0]):
    """One probability path: central line plus recovery-assumption wash."""
    ax.fill_between(bands.index, bands.min(axis=1), bands.max(axis=1),
                    color=color, alpha=0.12, lw=0, zorder=2)
    ax.plot(bands.index, bands[central], color=color, label=label, zorder=3)
    ax.set_ylim(0, 1.0)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    year_ticks(ax)
    ax.margins(x=0.01)
    return ax


def save_fig(fig, path, footnote: str | None = None):
    """Save with an optional muted footnote (event key, source note)."""
    if footnote:
        fig.text(0.02, -0.005, footnote, va="top", ha="left",
                 fontsize=7.5, color=INK2, linespacing=1.5)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
