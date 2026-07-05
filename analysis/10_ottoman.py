"""The Ottoman decline, 1869-1929: sixty years of Ottoman debt in London.

Three regimes, three series:

1869-1889  5% General Debt of 1865, the largest unsecured issue: carries
           the 1875-76 default, the Russo-Turkish war of 1877-78 and the
           1881 Muharrem restructuring. The 6% 1858 (customs-secured) and
           the 4% 1855 (Anglo-French-guaranteed) trade alongside it and
           identify *what* the market feared: the guaranteed bond never
           moved, the secured bond fell by half, the unsecured one lost
           80%+ - a decomposition of Ottoman risk into its collateral
           tiers.
1889-1904  the Muharrem "Converted Series A/B" administered by the
           Ottoman Public Debt Administration (OPDA).
1904-1929  the 4% Unified Debt: Young Turk revolution, Libya, the Balkan
           wars, WWI (London quotes cease mid-1916), Lausanne and the 1928
           Paris service agreement.

Because service (not battlefield victory) is the priced event, the
two-state model reads P(full service); the 1875 default realises the
"loss" state and the Muharrem terms (~50% writedown) pin the recovery
assumption ex post.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import imm_series, load_events, load_nber, save_fig, save_table
from bondwar import event_study as es
from bondwar import probability as pr
from bondwar import plotting as bp

events = load_events("ottoman")
nber = load_nber()
consols = nber["uk_consols"] / 100.0

gd = imm_series("Turkey", "5% General Debt 1865")
customs = imm_series("Turkey", "6% Loan 1858 (Customs)")
guaranteed = imm_series("Turkey", "4% 1855 (Anglo-French guarantee)")
converted = imm_series("Turkey", "Converted (Muharrem) Series A/B")
unified = imm_series("Turkey", "4% Unified Debt")

# ------------------------------------------------------------- figure ----
key_events = bp.select_events(events, names=[
    "Herzegovina", "Ramazan", "Full suspension", "Russia declares",
    "Plevna falls", "San Stefano", "Congress of Berlin", "Muharrem",
    "Young Turk", "Italy declares", "First Balkan War", "Ottoman fleet",
    "Mudros", "Lausanne", "Paris agreement"], max_events=15)

fig, axes = plt.subplots(2, 1, figsize=(12.5, 10),
                         gridspec_kw={"height_ratios": [1.5, 1.0],
                                      "hspace": 0.4})
bp.annotated_series(
    axes[0],
    {"5% General Debt 1865 (unsecured)": gd,
     "6% 1858 (customs-secured)": customs,
     "4% 1855 (Anglo-French guarantee)": guaranteed,
     "Converted Series A/B (OPDA)": converted,
     "4% Unified Debt": unified},
    events=key_events,
    colors={"5% General Debt 1865 (unsecured)": bp.PALETTE[0],
            "6% 1858 (customs-secured)": bp.PALETTE[1],
            "4% 1855 (Anglo-French guarantee)": bp.PALETTE[3],
            "Converted Series A/B (OPDA)": bp.PALETTE[2],
            "4% Unified Debt": bp.PALETTE[4]},
    ylabel="Price (% of par), London",
    title="Ottoman debt in London through the empire's decline, 1869-1929")
axes[0].set_ylim(0, 115)

# P(full service) for the unsecured General Debt up to the Muharrem decree.
# ~30y scheduled redemption; the realised loss state (post-1876 trading in
# the teens, harsh conversion terms for unsecured paper under Muharrem)
# pins recovery low, so the band spans 0-30%.
bands = pr.prob_bands(gd.loc[:"1881-12-31"], consols, coupon_rate=0.05,
                      maturity_years=30, recoveries=(0.0, 0.15, 0.3))
ax = axes[1]
bp.prob_band(ax, bands, "recovery_15pct",
             "P(full service), 5% General Debt", color=bp.PALETTE[0])
ax.set_ylim(0, 0.6)
ax.set_yticks([0, 0.2, 0.4, 0.6])
bp.mark_events(ax, key_events[key_events.date < "1883"], numbered=False)
ax.set_ylabel("Implied P(full service)")
ax.set_title("The market called the 1875 default years ahead", fontsize=10)
ax.legend(loc="upper right")
save_fig(fig, "ottoman_probabilities",
         footnote="Two-state model against UK consols, 30y redemption. "
                  "Line: 15% recovery; shading 0-30% (unsecured paper fared "
                  "worst in the Muharrem conversion).\n"
                  + bp.event_key(key_events))

# -------------------------------------------------------- event studies ----
moves = es.largest_moves(gd, k=12)
save_table(es.match_events(moves, events, tolerance_days=45),
           "ottoman_generaldebt_largest_moves")
print(f"General Debt chance-match baseline: "
      f"{es.chance_match_rate(gd, events, 45):.0%}")

car = es.event_window_study(
    gd, events[(events.major == 1) & (events.date < "1890")], pre=1, post=2)
save_table(car.set_index("event"), "ottoman_generaldebt_event_windows")

moves_u = es.largest_moves(unified, k=12)
save_table(es.match_events(moves_u, events, tolerance_days=45),
           "ottoman_unified_largest_moves")
print(f"Unified Debt chance-match baseline: "
      f"{es.chance_match_rate(unified, events, 45):.0%}")
car_u = es.event_window_study(
    unified, events[(events.major == 1) & (events.date >= "1904")],
    pre=1, post=2)
save_table(car_u.set_index("event"), "ottoman_unified_event_windows")

# ------------------------------------------------------------ narrative ----
print("\nCollateral-tier decomposition (level at date):")
for label, d in [("calm (Jun 1872)", "1872-06-30"),
                 ("Herzegovina rising (Sep 1875)", "1875-09-30"),
                 ("Ramazan default (Oct 1875)", "1875-10-31"),
                 ("suspension (Jun 1876)", "1876-06-30"),
                 ("Plevna falls (Dec 1877)", "1877-12-31"),
                 ("San Stefano (Mar 1878)", "1878-03-31"),
                 ("Congress of Berlin (Jul 1878)", "1878-07-31"),
                 ("Muharrem decree (Dec 1881)", "1881-12-31")]:
    row = []
    for name, s in [("unsecured", gd), ("customs", customs),
                    ("guaranteed", guaranteed)]:
        v = s.loc[:d].iloc[-1] if len(s.loc[:d]) else np.nan
        row.append(f"{name} {v:5.1f}")
    print(f"  {label}: " + " | ".join(row))

print("\n4% Unified Debt, key levels:")
for label, d in [("pre-revolution (Jun 1908)", "1908-06-30"),
                 ("Young Turks (Sep 1908)", "1908-09-30"),
                 ("Italy declares war (Oct 1911)", "1911-10-31"),
                 ("First Balkan War (Nov 1912)", "1912-11-30"),
                 ("entry to WW1 (Nov 1914)", "1914-11-30"),
                 ("last wartime quote (Jul 1916)", "1916-07-31"),
                 ("Mudros aftermath (Jan 1919)", "1919-01-31"),
                 ("Lausanne (Aug 1923)", "1923-08-31"),
                 ("Paris agreement (Jun 1928)", "1928-06-30"),
                 ("end of sample (Dec 1929)", "1929-12-31")]:
    s = unified.loc[:d]
    if len(s):
        print(f"  {label}: {s.iloc[-1]:.1f}")
