"""Russian Civil War: repudiated Tsarist bonds in London, 1917-1923.

After the Bolshevik repudiation decree (Feb 1918) the Russian 5% 1906 had
value only if (a) the Whites won and honored the Tsarist debt, (b) the
Soviets fell or settled with bondholders, or (c) a foreign power bailed
holders out (the 'peso problem' of Landon-Lane & Oosterlinck 2006). The
two-state model therefore reads the price as

    P_t = pi_t * V_honor + (1 - pi_t) * V_soviet

with pi_t the probability of a White victory *or equivalent settlement*,
V_honor the bond's value under a debt-honoring government, and V_soviet
residual value under a consolidated Soviet state (near zero ex post, but
held above zero for years by settlement hopes - hence the recovery band).
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import imm_series, load_events, load_nber, save_fig, save_table
from bondwar import event_study as es
from bondwar import probability as pr
from bondwar.plotting import annotated_series

events = load_events("russian_civil_war")
nber = load_nber()
consols = nber["uk_consols"] / 100.0

START, END = "1917-01-01", "1923-12-31"
rus = imm_series("Russia", "5% State Loan 1906", START, END)
rus45 = imm_series("Russia", "4.5% Loan 1909", START, END)

bands = pr.prob_bands(rus, consols, coupon_rate=0.05, maturity_years=40,
                      recoveries=(0.0, 0.1, 0.25))

fig, axes = plt.subplots(2, 1, figsize=(12.5, 10.5), sharex=True)
annotated_series(axes[0],
                 {"Russia 5% 1906": rus, "Russia 4.5% 1909": rus45},
                 events=events, ylabel="price (% of par), London",
                 title="Repudiated Tsarist bonds during the Russian Civil War")
axes[1].fill_between(bands.index, bands.min(axis=1), bands.max(axis=1),
                     alpha=0.25)
axes[1].plot(bands["recovery_10pct"], lw=1.8,
             label="P(White victory / debt-honoring settlement)")
for _, r in events[events.major == 1].iterrows():
    axes[1].axvline(r.date, color="grey", ls="--", lw=0.7, alpha=0.6)
axes[1].set_ylim(0, 1.0)
axes[1].set_ylabel("implied probability")
axes[1].legend(fontsize=8)
axes[1].set_title("Implied probability that the repudiation would be undone")
save_fig(fig, "rcw_probabilities")

moves = es.largest_moves(rus, k=14)
save_table(es.match_events(moves, events, tolerance_days=45),
           "rcw_largest_moves")
car = es.event_window_study(rus, events[events.major == 1], pre=1, post=2)
save_table(car.set_index("event"), "rcw_event_windows")

p = bands["recovery_10pct"]
for label, d in [("Feb 1918 (repudiation)", "1918-02-28"),
                 ("Jun 1919 (Denikin advancing)", "1919-06-30"),
                 ("Oct 1919 (Orel/Petrograd high-water)", "1919-10-31"),
                 ("Mar 1920 (Denikin broken)", "1920-03-31"),
                 ("Nov 1920 (Wrangel evacuates)", "1920-11-30"),
                 ("Dec 1922 (after Genoa/Rapallo)", "1922-12-31")]:
    if d in p.index.strftime("%Y-%m-%d").tolist():
        print(f"{label}: price {rus.loc[d]:.1f}, implied prob {p.loc[d]:.0%}")
print(es.match_events(moves, events, tolerance_days=45)[
    ["pct_change", "candidate_event"]].to_string())
