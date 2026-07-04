"""US Civil War: Union greenbacks (NY gold room) and Confederate gold
bonds (Amsterdam) -> market-implied victory probabilities + event study.

Union side. Greenbacks were inconvertible paper whose specie value hinged
on eventual resumption, which contemporaries tied to Union victory at
bearable fiscal cost. Two-state model on the gold value of $100 in
greenbacks with V_win = 100 discounted for a resumption delay, and V_lose
calibrated to a Union that survives a lost war (the Union would not have
vanished, so V_lose >> 0). Because V_lose is the shakiest input we show a
band.

Confederate side. Monthly Amsterdam prices of the CSA 8% gold bonds
(literature-anchored series, see data/manual/PROVENANCE.md), valued as a
10-year 8% semiannual coupon bond discounted at the mid-1860s UK consol
yield, with recovery zero on defeat (Weidenmier-Oosterlinck baseline).
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import MANUAL, PROCESSED, load_events, save_fig, save_table
from bondwar import event_study as es
from bondwar import probability as pr
from bondwar.plotting import annotated_series

CONSOL_YIELD_1860s = 0.033  # UK consols averaged ~3.2-3.4% 1862-65 (Homer & Sylla)

events = load_events("us_civil_war")

# ---------------------------------------------------------------- Union ----
gb = pd.read_csv(PROCESSED / "greenback_monthly.csv", parse_dates=["date"]
                 ).set_index("date")["greenback_gold_value"]

# V_win: $100 greenback redeemed at par after a ~4-year resumption delay
v_win = 100 * (1 + CONSOL_YIELD_1860s) ** -4          # ~87.8
scenarios = {"v_lose_25": 25.0, "v_lose_40": 40.0, "v_lose_55": 55.0}
union_bands = pd.DataFrame({
    k: pr.implied_prob(gb, v_win, v)
    for k, v in scenarios.items()})

# ---------------------------------------------------------- Confederacy ----
csa = pd.read_csv(MANUAL / "confederate_amsterdam_monthly.csv",
                  parse_dates=["date"]).set_index("date")["price_gold_dollars"]
csa_bands = pr.prob_bands(csa, CONSOL_YIELD_1860s, coupon_rate=0.08,
                          maturity_years=10, recoveries=(0.0, 0.1, 0.2))
# replicate the paper's headline: price 60 pre-Gettysburg -> ~42%
v_win_csa = pr.bond_pv(0.08, 10, CONSOL_YIELD_1860s)
print(f"CSA bond V_win={v_win_csa:.1f}; pi at P=60: {60 / v_win_csa:.2%} "
      "(Weidenmier-Oosterlinck report ~42%)")

# ------------------------------------------------------------- figures ----
fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
annotated_series(axes[0],
                 {"Gold value of $100 greenbacks (NY)": gb,
                  "CSA 8% gold bond, Amsterdam (gold $)": csa},
                 events=events, ylabel="price / specie value",
                 title="US Civil War: the two sides' war paper")
mid_u = union_bands["v_lose_40"]
axes[1].fill_between(union_bands.index, union_bands.min(axis=1),
                     union_bands.max(axis=1), alpha=0.25)
axes[1].plot(mid_u, lw=1.8, label="P(Union victory w/ resumption)")
mid_c = csa_bands.iloc[:, 1]
axes[1].fill_between(csa_bands.index, csa_bands.min(axis=1),
                     csa_bands.max(axis=1), alpha=0.25, color="firebrick")
axes[1].plot(mid_c, lw=1.8, color="firebrick", label="P(Confederate victory)")
for _, r in events[events.major == 1].iterrows():
    axes[1].axvline(r.date, color="grey", ls="--", lw=0.7, alpha=0.6)
axes[1].set_ylim(0, 1.02)
axes[1].set_ylabel("market-implied probability")
axes[1].legend(fontsize=8)
axes[1].set_title("Implied victory probabilities (bands = alternative "
                  "recovery/resumption assumptions)")
save_fig(fig, "civilwar_probabilities")

# ---------------------------------------------------------- event study ----
moves = es.largest_moves(gb, k=12)
matched = es.match_events(moves, events, tolerance_days=40)
save_table(matched, "civilwar_greenback_largest_moves")

car = es.event_window_study(gb, events[events.major == 1], pre=1, post=1)
save_table(car.set_index("event"), "civilwar_greenback_event_windows")

car_csa = es.event_window_study(csa, events[(events.major == 1)
                                            & (events.date >= "1863-06-01")],
                                pre=1, post=1)
save_table(car_csa.set_index("event"), "civilwar_csa_event_windows")

print(matched.to_string())
