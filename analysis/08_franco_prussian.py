"""Franco-Prussian War, 1870-71: French rentes and the North German
Confederation's war loan in London (Investor's Monthly Manual).

Both sides' debt survived this war: France famously serviced the rentes
throughout the war, the Commune, and the 5bn-franc indemnity. So the
two-state victory model does not apply as it does for repudiation cases;
what the London market priced was the *fiscal burden of losing* - the
indemnity, occupation costs and political chaos - plus, in the worst
months, some probability of revolutionary default. We therefore read the
rente price primarily as a war-burden discount and run the event study on
its changes, reporting an implied P(full service) band only as an upper
bound diagnostic.

The German contrast: the North German Confederation floated a 5% loan in
London in 1870; it never traded below 98 during the entire conflict. The
NBER German bond-yield series (m13028a, monthly from Jan 1870) confirms
the war barely moved Berlin's cost of capital.
"""

import matplotlib.pyplot as plt
import numpy as np

from common import imm_series, load_events, load_nber, save_fig, save_table
from bondwar import event_study as es
from bondwar import probability as pr
from bondwar import plotting as bp

events = load_events("franco_prussian")
nber = load_nber()
consols = nber["uk_consols"] / 100.0

START, END = "1869-01-01", "1874-12-31"
rentes = imm_series("France", "3% Rentes", START, END)
morgan = imm_series("France", "6% Morgan Loan 1870", START, END)
ngc = imm_series("North German Confederation", "5% Loan 1870", START, END)
germany_yield = nber["germany_yields"].loc[START:END]

# ------------------------------------------------------------- figure ----
key_events = bp.select_events(events, names=[
    "declares war", "Woerth", "Sedan", "Republic", "Siege of Paris",
    "Morgan loan", "Metz", "Empire proclaimed", "Paris capitulates",
    "indemnity", "Commune", "Thiers rente"])

fig, axes = plt.subplots(2, 1, figsize=(11.5, 9), sharex=False,
                         gridspec_kw={"height_ratios": [1.6, 1.0],
                                      "hspace": 0.42})
bp.annotated_series(
    axes[0],
    {"France 3% rentes": rentes, "France 6% Morgan loan 1870": morgan,
     "North German Confederation 5% 1870": ngc},
    events=key_events,
    colors={"France 3% rentes": bp.PALETTE[0],
            "France 6% Morgan loan 1870": bp.PALETTE[2],
            "North German Confederation 5% 1870": bp.PALETTE[1]},
    ylabel="Price (% of par), London",
    title="Franco-Prussian War: both sides' debt in London, 1869-74")
axes[0].set_ylim(45, 110)

ax2 = axes[1]
ax2.plot(germany_yield.index, germany_yield.values, color=bp.PALETTE[1],
         label="German bond yield (NBER m13028a)")
ry = 3.0 / rentes * 100  # current yield on the 3% rente
ax2.plot(ry.index, ry.values, color=bp.PALETTE[0],
         label="French 3% rente current yield (London price)")
bp.mark_events(ax2, key_events, numbered=False)
ax2.set_ylabel("Yield, % p.a.")
ax2.set_title("The asymmetry of the war's cost of capital", fontsize=10)
ax2.legend(loc="upper left")
bp.year_ticks(ax2)
ax2.margins(x=0.01)
save_fig(fig, "franco_prussian_prices",
         footnote="IMM London month-end quotes; rente quotes suspended "
                  "Jan-Mar 1871 (siege/Commune).\n" + bp.event_key(key_events))

# --------------------------------------------------------- event study ----
moves = es.largest_moves(rentes, k=12)
save_table(es.match_events(moves, events, tolerance_days=45),
           "franco_prussian_largest_moves")
print(f"chance-match baseline (any month, 45-day rule): "
      f"{es.chance_match_rate(rentes, events, 45):.0%}")

car = es.event_window_study(rentes, events[events.major == 1], pre=1, post=2)
save_table(car.set_index("event"), "franco_prussian_event_windows")

# -------------------------------------- war-burden discount + level line ----
# Upper-bound service probability from the two-state model (perpetuity).
bands = pr.prob_bands(rentes, consols, coupon_rate=0.03, maturity_years=None,
                      recoveries=(0.0, 0.25, 0.5))
print("\nWar-burden narrative (3% rentes, London):")
for label, d in [("Pre-candidature (Jun 1870)", "1870-06-30"),
                 ("After Sedan (Sep 1870)", "1870-09-30"),
                 ("Siege of Paris (Nov 1870)", "1870-11-30"),
                 ("Armistice/indemnity (Apr 1871)", "1871-04-30"),
                 ("Commune crushed (Jun 1871)", "1871-06-30"),
                 ("First Thiers loan (Jul 1871)", "1871-07-31"),
                 ("Indemnity paid off (Sep 1873)", "1873-09-30")]:
    if d in rentes.index.strftime("%Y-%m-%d").tolist():
        p25 = bands["recovery_25pct"].loc[d]
        print(f"  {label}: price {rentes.loc[d]:5.1f}, "
              f"implied P(full service) ~{p25:.0%} (25% recovery)")

peak_to_trough = (rentes.loc["1870-11-30"] / rentes.loc["1870-06-30"] - 1) * 100
print(f"\nRente drawdown Jun->Nov 1870: {peak_to_trough:+.1f}%")
if len(ngc):
    print(f"NGC 5% 1870 range while quoted: "
          f"{ngc.min():.1f}..{ngc.max():.1f} (never a war discount)")
print(f"German yield Jul 1870 {germany_yield.loc['1870-07-31']:.2f}% -> "
      f"peak {germany_yield.loc['1870-07-31':'1871-06-30'].max():.2f}% -> "
      f"Jun 1871 {germany_yield.loc['1871-06-30']:.2f}%")
