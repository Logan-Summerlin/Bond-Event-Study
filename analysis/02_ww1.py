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
from bondwar.plotting import annotated_series

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
fig, axes = plt.subplots(2, 1, figsize=(12.5, 10.5), sharex=True)
annotated_series(axes[0], series, events=events,
                 ylabel="price (% of par), London",
                 title="WW1 belligerents' bonds in London (IMM monthly)")
colors = dict(zip(series, plt.rcParams["axes.prop_cycle"].by_key()["color"]))
for name in series:
    b = bands[name]
    axes[1].fill_between(b.index, b.min(axis=1), b.max(axis=1),
                         alpha=0.18, color=colors[name])
    axes[1].plot(b["recovery_25pct"], lw=1.7, color=colors[name], label=name)
for _, r in events[events.major == 1].iterrows():
    axes[1].axvline(r.date, color="grey", ls="--", lw=0.6, alpha=0.5)
axes[1].set_ylim(0, 1.05)
axes[1].set_ylabel("implied P(debt survival) = P(no defeat-driven default)")
axes[1].legend(fontsize=8)
axes[1].set_title("Two-state model, recovery 0-50% bands "
                  "(central line: 25% recovery)")
save_fig(fig, "ww1_probabilities")

# ----------------------------------------- Russia close-up & Brusilov ----
rus = series["Russia 5% 1906"]
fig2, ax = plt.subplots(figsize=(12.5, 6))
annotated_series(ax, {"Russia 5% 1906 (London)": rus},
                 events=events[events.event.str.contains(
                     "Tannenberg|Straits|Gorlice|Warsaw|Brusilov|Romania|"
                     "February|Kerensky|October|repudiation|Brest",
                     case=False)],
                 ylabel="price (% of par)",
                 title="Russian Imperial 5% 1906 through the Great War")
save_fig(fig2, "ww1_russia_closeup")

moves = es.largest_moves(rus, k=12)
save_table(es.match_events(moves, events, tolerance_days=45),
           "ww1_russia_largest_moves")

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
