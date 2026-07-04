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
from bondwar import plotting as bp

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
key_events = bp.select_events(events, names=[
    "Sumter", "Seven Days", "Antietam", "Gettysburg", "Chickamauga",
    "Wilderness", "Early's army", "Fall of Atlanta", "re-elected",
    "Richmond falls"])

fig, axes = plt.subplots(2, 1, figsize=(11, 9), sharex=True)
bp.annotated_series(axes[0],
                    {"Gold value of $100 greenbacks (New York)": gb,
                     "CSA 8% gold bond, Amsterdam (gold $)": csa},
                    events=key_events, ylabel="Price / specie value",
                    title="US Civil War: the two sides' war paper",
                    colors={"Gold value of $100 greenbacks (New York)": bp.UNION_BLUE,
                            "CSA 8% gold bond, Amsterdam (gold $)": bp.CSA_RED})
bp.prob_band(axes[1], union_bands, "v_lose_40",
             "P(Union victory with resumption)", color=bp.UNION_BLUE)
bp.prob_band(axes[1], csa_bands, csa_bands.columns[1],
             "P(Confederate victory)", color=bp.CSA_RED)
bp.mark_events(axes[1], key_events, numbered=False)
axes[1].set_ylabel("Market-implied probability")
axes[1].legend(loc="upper right")
axes[1].set_title("Implied victory probabilities "
                  "(shading: alternative recovery/resumption assumptions)")
save_fig(fig, "civilwar_probabilities", footnote=bp.event_key(key_events))

# ---------------------------------------------------------- event study ----
moves = es.largest_moves(gb, k=12)
matched = es.match_events(moves, events, tolerance_days=40)
save_table(matched, "civilwar_greenback_largest_moves")
print(f"chance-match baseline (any month, 40-day rule): "
      f"{es.chance_match_rate(gb, events, 40):.0%}")
pi_raw = pr.implied_prob(gb, v_win, scenarios['v_lose_40'], clip=False)
print(f"share of months where the two-state inversion clips: "
      f"{pr.clipped_share(pi_raw):.1%}")

car = es.event_window_study(gb, events[events.major == 1], pre=1, post=1)
save_table(car.set_index("event"), "civilwar_greenback_event_windows")

car_csa = es.event_window_study(csa, events[(events.major == 1)
                                            & (events.date >= "1863-06-01")],
                                pre=1, post=1)
save_table(car_csa.set_index("event"), "civilwar_csa_event_windows")

print(matched.to_string())
