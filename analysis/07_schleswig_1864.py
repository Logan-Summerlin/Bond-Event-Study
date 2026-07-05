"""Denmark and the Schleswig-Holstein crisis, 1863-65.

Data: hand-collected London bargain prices of three Danish loans (the 3%
of 1825, the 4% of 1863 and the 5% war loan of January 1864) read from
page scans of The Economist's Bankers' Price Current
(data/manual/danish_london_1862_1865.csv, see PROVENANCE.md), against the
UK 3% consol yield (NBER m13041b).

Two findings, one substantive and one methodological:

1. Denmark's credit took a measurable but *bounded* hit: the 3% 1825 fell
   from 84 (Dec 1863) to 74 (early Sep 1864, after the peace preliminaries
   ceded two-fifths of the monarchy) and had recovered to ~80 within six
   months of the Treaty of Vienna; the 4% 1863 traced 91.5 -> 80 -> 85.
   London never priced Danish default as likely - defeat repriced Denmark
   as a smaller, weaker, but still good credit. The war loan floated *in*
   London in Jan 1864 at 93 stood at 95.5 while the London Conference sat,
   dipped to ~91 when the war resumed, and rallied to 98 by March 1865.
2. The market itself nearly shut: in most crisis weeks - including the
   whole invasion phase Feb-Apr 1864 - The Economist marks *no* Danish
   bargains at all. Wartime illiquidity is itself the signal, and any
   'probability path' from such a book would be false precision. We
   therefore report levels, between-bargain moves, and the implied
   default-probability *bound*, not a monthly probability line.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import MANUAL, load_events, load_nber, save_fig, save_table
from bondwar import probability as pr
from bondwar import plotting as bp

events = load_events("schleswig_1864")
nber = load_nber()
consols = nber["uk_consols"] / 100.0

df = pd.read_csv(MANUAL / "danish_london_1862_1865.csv",
                 parse_dates=["date"])
series = {name: g.set_index("date")["price"].sort_index()
          for name, g in df.groupby("series")}

# ------------------------------------------------------------- figure ----
key_events = bp.select_events(events, names=[
    "November Constitution incorporating", "Frederik VII dies",
    "federal execution", "war loan", "ultimatum", "cross the Eider",
    "Dannevirke", "Dybboel", "London Conference opens", "collapses",
    "Als island", "preliminaries", "Treaty of Vienna"], max_events=14)

fig, ax = plt.subplots(figsize=(11.5, 6))
colors = {"3% 1825": bp.PALETTE[0], "4% Loan 1863": bp.PALETTE[1],
          "5% Loan 1864": bp.PALETTE[2]}
for name, s in series.items():
    ax.plot(s.index, s.values, marker="o", ms=4.5, lw=1.4, alpha=0.9,
            color=colors[name], label=f"Danish {name}")
bp.mark_events(ax, key_events)
ax.set_ylabel("Price (% of par), London bargains")
ax.set_title("Danish bonds in London through the Schleswig-Holstein "
             "crisis and the war of 1864", pad=36)
ax.legend(loc="lower left")
bp.year_ticks(ax)
ax.margins(x=0.03)
save_fig(fig, "schleswig_danish_bonds",
         footnote="Markers are individual bargains from The Economist's "
                  "Bankers' Price Current; gaps are weeks with no marked "
                  "Danish business (most of the war).\n"
                  + bp.event_key(key_events))

# ----------------------------------------------- between-bargain moves ----
rows = []
for name, s in series.items():
    r = np.log(s).diff().dropna()
    for dt, v in r.items():
        prev = s.index[s.index.get_loc(dt) - 1]
        cand = events[(events.date <= dt)].iloc[-1] if len(
            events[events.date <= dt]) else None
        rows.append({
            "series": name, "from": prev.date(), "to": dt.date(),
            "pct_change": (np.exp(v) - 1) * 100,
            "last_event_before": None if cand is None else cand["event"],
        })
moves = (pd.DataFrame(rows)
         .sort_values("pct_change", key=lambda s: s.abs(), ascending=False))
save_table(moves.set_index("to").head(12), "schleswig_largest_moves")

# --------------------------------------- default-probability bound ----
# Two-state read on the 3% 1825 (perpetuity). Denmark's post-1813
# record was clean; assume recovery 25-50% if the war had somehow ended
# in fiscal catastrophe.
s3 = series["3% 1825"]
rf = consols.reindex(s3.index, method="ffill")
print("3% 1825: implied P(full service) under the two-state model")
for rec in (0.25, 0.5):
    pi = pr.implied_prob_series(s3, consols, 0.03, None, recovery_frac=rec)
    lo, hi = pi.min(), pi.max()
    print(f"  recovery {rec:.0%}: P ranges {lo:.0%} (worst bargain) "
          f"to {hi:.0%}")
worst = s3.idxmin()
print(f"  worst mark: {s3.min():.1f} on {worst.date()} "
      f"(after the peace preliminaries ceded the duchies)")

# yield-spread view (current yield minus consols), per bargain
print("\nCurrent-yield spread over consols (basis points):")
for name, cpn in [("3% 1825", 3.0), ("4% Loan 1863", 4.0),
                  ("5% Loan 1864", 5.0)]:
    s = series[name]
    cy = cpn / s * 100
    sp = (cy / 100 - consols.reindex(s.index, method="ffill")) * 1e4
    print(f"  {name}: {sp.iloc[0]:.0f}bp ({s.index[0].date()}) -> "
          f"peak {sp.max():.0f}bp -> {sp.iloc[-1]:.0f}bp ({s.index[-1].date()})")

n_weeks = 82
print(f"\nLiquidity finding: of ~{n_weeks} Economist issues examined "
      f"1862-65, only {df.source_issue.nunique()} contain any marked "
      f"Danish bargain; none at all between 1864-01-23 and 1864-05-21 "
      f"(the invasion, Dannevirke, and Dybboel) except the new war "
      f"loan's scrip.")
