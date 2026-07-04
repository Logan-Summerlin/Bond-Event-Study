"""World War II: belligerent & occupied-country bonds on neutral exchanges
(Zurich, Stockholm), monthly 1933-48, from Frey & Waldenström (2004, 2008).

German bonds in Zurich price the Reich's willingness/ability to service
external debt - which after 1939 is dominated by war fortunes: a German
*victory* meant repayment of (Swiss-held) German bonds, defeat meant
worthlessness (as realized: ~15% of par in 1948). French and Belgian
bonds price the survival of those states' finances under German attack /
occupation. Germany was already in partial external default after 1933-34,
so its "V_win" is calibrated to the pre-war trading range rather than par.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import PROCESSED, load_events, save_fig, save_table
from bondwar import event_study as es
from bondwar import probability as pr
from bondwar import plotting as bp

events = load_events("ww2")
ww2 = pd.read_csv(PROCESSED / "ww2_bond_prices.csv", parse_dates=["date"])


def get(market, issuer):
    s = (ww2[(ww2.market == market) & (ww2.issuer == issuer)]
         .set_index("date")["price"].sort_index())
    return s


zh = {c: get("Zurich", c) for c in ["Germany", "France", "Belgium"]}
st = {c: get("Stockholm", c) for c in ["Germany", "Belgium"]}

# V_win anchors: mean price over 1936-38 (pre-war "as-good-as-it-gets"
# level given Germany's existing transfer restrictions); V_lose bands.
anchors = {}
bands = {}
for name, s in zh.items():
    v_win = s.loc["1936-01-01":"1938-06-30"].mean()
    anchors[name] = v_win
    war = s.loc["1938-01-01":"1945-12-31"]
    bands[name] = pd.DataFrame({
        f"v_lose_{v}": pr.implied_prob(war, v_win, v)
        for v in (0.0, 10.0, 20.0)})
    print(f"Zurich {name}: V_win anchor = {v_win:.1f}")

key_events = bp.select_events(events, names=[
    "Munich", "invades Poland", "Fall of France", "Battle of Britain",
    "Barbarossa", "Pearl Harbor", "Stalingrad", "D-Day", "Ardennes",
    "unconditional surrender"])
series_map = ({f"{k} (Zurich)": v for k, v in zh.items()}
              | {f"{k} (Stockholm)": v for k, v in st.items()})
colors = dict(zip(series_map, bp.PALETTE))

fig = plt.figure(figsize=(11.5, 10.5))
gs = fig.add_gridspec(2, 3, height_ratios=[1.5, 0.8],
                      hspace=0.4, wspace=0.22)
ax_top = fig.add_subplot(gs[0, :])
bp.annotated_series(ax_top, series_map, events=key_events, colors=colors,
                    ylabel="Bond price index",
                    title="WW2 sovereign bonds on neutral exchanges, 1933-48")
# small multiples: one probability path per issuer (Zurich)
for i, (name, b) in enumerate(bands.items()):
    ax = fig.add_subplot(gs[1, i])
    bp.prob_band(ax, b, "v_lose_10.0", name,
                 color=colors[f"{name} (Zurich)"])
    bp.mark_events(ax, key_events, numbered=False)
    bp.year_ticks(ax, step=2)
    ax.set_title(f"{name}: P(no defeat-driven default)", fontsize=9.5, pad=6)
    if i == 0:
        ax.set_ylabel("Implied probability")
save_fig(fig, "ww2_probabilities",
         footnote="Two-state model against each issuer's 1936-38 Zurich "
                  "price anchor (V_win). Line: recovery 10 on defeat; "
                  "shading spans recovery 0-20.\n" + bp.event_key(key_events))

for name, s in zh.items():
    war = s.loc["1938-01-01":"1945-12-31"]
    raw = pr.implied_prob(war, anchors[name], 10.0, clip=False)
    print(f"{name}: share of war months where the inversion clips "
          f"(price outside [V_lose, V_win]): {pr.clipped_share(raw):.0%}")
print(f"chance-match baseline (any month, 45-day rule): "
      f"{es.chance_match_rate(zh['Germany'].loc['1938':'1945'], events, 45):.0%}")

# --------------------------------------------------------- event study ----
for name, s in zh.items():
    moves = es.largest_moves(s.loc["1938-01-01":"1945-12-31"], k=12)
    save_table(es.match_events(moves, events, tolerance_days=45),
               f"ww2_{name.lower()}_largest_moves")

car = es.event_window_study(zh["Germany"].loc["1938-01-01":"1945-12-31"],
                            events[events.major == 1], pre=1, post=2)
save_table(car.set_index("event"), "ww2_germany_event_windows")

print("\nGermany (Zurich) largest moves:")
print(es.match_events(es.largest_moves(
    zh["Germany"].loc["1938-01-01":"1945-12-31"], k=12), events,
    tolerance_days=45)[["pct_change", "candidate_event"]].to_string())
g = bands["Germany"]["v_lose_10.0"]
for label, d in [("Munich (Sep 38)", "1938-09-30"),
                 ("war begins (Sep 39)", "1939-09-30"),
                 ("fall of France (Jun 40)", "1940-06-30"),
                 ("pre-Barbarossa (May 41)", "1941-05-31"),
                 ("post-Stalingrad (Feb 43)", "1943-02-28"),
                 ("post-D-Day (Jun 44)", "1944-06-30"),
                 ("Jan 45", "1945-01-31")]:
    if pd.Timestamp(d) in g.index:
        print(f"  implied P(German debt survival) {label}: {g.loc[d]:.0%}")
