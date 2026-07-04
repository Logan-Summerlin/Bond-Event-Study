"""Shared plotting helpers: annotated price series and probability bands."""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams.update({
    "figure.figsize": (12, 6.5),
    "figure.dpi": 130,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.size": 10,
})


def annotated_series(ax, series_map: dict[str, pd.Series],
                     events: pd.DataFrame | None = None,
                     max_labels: int = 14, ylabel: str = "",
                     title: str = ""):
    """Plot one or more series with vertical event markers."""
    for label, s in series_map.items():
        ax.plot(s.index, s.values, lw=1.6, label=label)
    if events is not None:
        ev = events.dropna(subset=["date"]).sort_values("date")
        if len(ev) > max_labels and "major" in ev.columns:
            ev = ev[ev["major"] == 1]
        ev = ev.head(max_labels)
        ymin, ymax = ax.get_ylim()
        for i, (_, row) in enumerate(ev.iterrows()):
            ax.axvline(row["date"], color="grey", ls="--", lw=0.8, alpha=0.7)
            ax.annotate(row["event"],
                        xy=(row["date"], ymax),
                        xytext=(2, -4 - 11 * (i % 4)),
                        textcoords="offset points",
                        rotation=0, fontsize=7, color="dimgrey",
                        ha="left", va="top", clip_on=True)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc="best", fontsize=8)
    return ax


def prob_band_plot(ax, bands: pd.DataFrame, label_prefix: str = "",
                   events: pd.DataFrame | None = None, title: str = ""):
    """Plot central probability path with min/max recovery band shading."""
    cols = list(bands.columns)
    mid = bands[cols[len(cols) // 2]]
    ax.fill_between(bands.index, bands.min(axis=1), bands.max(axis=1),
                    alpha=0.25, label=f"{label_prefix} recovery-assumption band")
    ax.plot(mid.index, mid.values, lw=1.8, label=f"{label_prefix} central estimate")
    if events is not None:
        for _, row in events.dropna(subset=["date"]).iterrows():
            ax.axvline(row["date"], color="grey", ls="--", lw=0.8, alpha=0.6)
    ax.set_ylim(0, 1.02)
    ax.set_ylabel("Market-implied probability")
    ax.set_title(title)
    ax.legend(loc="best", fontsize=8)
    return ax
