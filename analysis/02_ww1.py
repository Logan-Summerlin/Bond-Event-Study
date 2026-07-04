"""World War I: belligerent sovereign bonds in London (Investor's Monthly
Manual) -> implied debt-survival probabilities + event study.

Focus: the Russian 5% State Loan of 1906, the empire's flagship external
bond, quoted in London continuously through the war. Benchmark: UK consol
yield (NBER m13041c). France (3% rentes), Germany (Imperial 3% 1891-3) and
Austria (4% gold rentes) are read the same way, with the caveat that
enemy-issuer quotes in wartime London are thin and sometimes stale, and
that early-war quotes sit under the Exchange's minimum-price rules.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import imm_series, load_events, load_nber, save_fig, save_table
from bondwar import event_study as es
from bondwar import probability as pr
from bondwar import plotting as bp

events = load_events("ww1")
nber = load_nber()
consols = nber["uk_consols"] / 100.0  # decimal yield

START, END = "1913-01-01", "1919-06-30"

series = {
    "Russia 5% 1906": imm_series("Russia", "5% State Loan 1906", START, END),
    "France 3% rentes": imm_series("France", "3% Rentes", START, END),
    "Germany Imperial 3%": imm_series("Germany", None, START, END),
    "Austria 4% gold rentes": imm_series("Austria", "4% Gold Rentes", START, END),
}
coupons = {"Russia 5% 1906": 0.05, "France 3% rentes": 0.03,
           "Germany Imperial 3%": 0.03, "Austria 4% gold rentes": 0.04}
# Russia 1906 was a 50-year loan (matures 1956); rentes are perpetual.
maturities = {"Russia 5% 1906": 42, "France 3% rentes": None,
              "Germany Imperial 3%": None, "Austria 4% gold rentes": None}

bands = {}
for name, s in series.items():
    bands[name] = pr.prob_bands(s, consols, coupons[name], maturities[name],
                                recoveries=(0.0, 0.25, 0.5))

# ------------------------------------------------------------- figures ----
key_events = bp.select_events(events, names=[
    "Britain enters", "Tannenberg", "Marne", "Gorlice", "Fall of Warsaw",
    "Brusilov Offensive begins", "Romania joins", "February Revolution",
    "United States declares", "October Revolution",
    "armistice at Brest-Litovsk"])
colors = dict(zip(series, bp.PALETTE))

fig = plt.figure(figsize=(11.5, 10.5))
gs = fig.add_gridspec(3, 2, height_ratios=[1.5, 0.75, 0.75],
                      hspace=0.45, wspace=0.18)
ax_top = fig.add_subplot(gs[0, :])
bp.annotated_series(ax_top, series, events=key_events, colors=colors,
                    ylabel="Price (% of par), London",
                    title="WW1 belligerents' bonds in London (IMM monthly)")
# probability paths as small multiples: four overlapping bands on one
# axis are unreadable, and each path only needs comparing with itself
for i, name in enumerate(series):
    ax = fig.add_subplot(gs[1 + i // 2, i % 2])
    bp.prob_band(ax, bands[name], "recovery_25pct", name, color=colors[name])
    bp.mark_events(ax, key_events, numbered=False)
    ax.set_title(name, fontsize=10, pad=6)
    if i % 2 == 0:
        ax.set_ylabel("Implied P(debt survival)")
save_fig(fig, "ww1_probabilities",
         footnote="Two-state model. Line: 25% recovery on defeat; "
                  "shading spans recovery assumptions 0-50%.\n"
                  + bp.event_key(key_events))

# ----------------------------------------- Russia close-up & Brusilov ----
rus = series["Russia 5% 1906"]
rus_events = bp.select_events(events, names=[
    "Tannenberg", "Straits", "Gorlice", "Warsaw", "Brusilov", "Romania",
    "February", "Kerensky", "October", "repudiation", "Brest"])
fig2, ax = plt.subplots(figsize=(11.5, 5.5))
bp.annotated_series(ax, {"Russia 5% 1906 (London)": rus}, events=rus_events,
                    ylabel="Price (% of par)",
                    title="Russian Imperial 5% 1906 through the Great War")
save_fig(fig2, "ww1_russia_closeup", footnote=bp.event_key(rus_events))

moves = es.largest_moves(rus, k=12)
save_table(es.match_events(moves, events, tolerance_days=45),
           "ww1_russia_largest_moves")
print(f"chance-match baseline (any month, 45-day rule): "
      f"{es.chance_match_rate(rus, events, 45):.0%}")

car = es.event_window_study(rus, events[events.major == 1], pre=1, post=2,
                            benchmark=None)
save_table(car.set_index("event"), "ww1_russia_event_windows")

# Brusilov Offensive window, explicitly (the user's motivating example)
win = rus.loc["1916-04-30":"1916-11-30"]
r = np.log(win).diff().dropna()
print("\nRussia 5% 1906 around the Brusilov Offensive (Jun 4 - Sep 20 1916):")
print(win.to_string())
print(f"cumulative move Jun-Sep 1916: "
      f"{(win.loc['1916-09-30'] / win.loc['1916-05-31'] - 1) * 100:+.1f}%")
b = bands["Russia 5% 1906"]["recovery_25pct"]
print(f"implied survival prob: {b.loc['1916-05-31']:.0%} (May 1916) -> "
      f"{b.loc['1916-09-30']:.0%} (Sep 1916)")

for name, s in series.items():
    print(f"{name}: {s.dropna().shape[0]} monthly obs "
          f"{s.dropna().index.min().date()}..{s.dropna().index.max().date()}")
