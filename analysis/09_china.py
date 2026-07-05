"""China, 1877-1929: Qing and Republican sterling debt in London (IMM).

China's foreign loans were secured on specific revenues collected under
foreign supervision (Imperial Maritime Customs, later the Salt
Administration). That security survived the fall of the dynasty: the
market event being priced is therefore not "does the emperor win" but
"does the revenue pledge keep paying whoever rules" - fiscal/institutional
survival rather than battlefield victory. The interesting historical
finding is which shocks the London market treated as threats to that
machinery (Boxer summer 1900, the warlord decade) and which it shrugged
off (the 1911 revolution itself).

Series: the Anglo-German indemnity loans of 1896 (5%, matures 1932) and
1898 (4.5%, matures 1943) for the Qing decades; the 5% Reorganisation Loan
of 1913 (matures 1960) for the Republic; early loans (8% 1874-6, 7% Series
A) and the defaulted 8% sterling Treasury notes of 1919-20 as context.
"""

import matplotlib.pyplot as plt
import numpy as np

from common import imm_series, load_events, load_nber, save_fig, save_table
from bondwar import event_study as es
from bondwar import probability as pr
from bondwar import plotting as bp

events = load_events("china")
nber = load_nber()
consols = nber["uk_consols"] / 100.0

series = {
    "7% Series A (1886)": imm_series("China", "7% Loan Series A"),
    "6% Gold 1895": imm_series("China", "6% Gold Loan 1895"),
    "5% Gold 1896": imm_series("China", "5% Gold Loan 1896"),
    "4.5% Gold 1898": imm_series("China", "4.5% Gold Loan 1898"),
    "5% Reorganisation 1913": imm_series("China", "5% Reorganisation Loan 1913"),
    "8% Treasury notes 1920s": imm_series("China", "8% Sterling Treasury 1920s"),
}

key_events = bp.select_events(events, names=[
    "Yalu", "Shimonoseki", "Kiaochow", "Boxer Rising", "Boxer Protocol",
    "Wuchang", "Abdication", "Reorganisation Loan", "Twenty-One",
    "Yuan Shikai dies", "Zhili-Fengtian war,", "May Thirtieth",
    "Northern Expedition", "Nationalists take Peking"], max_events=14)

colors = dict(zip(series, bp.PALETTE))
fig, axes = plt.subplots(2, 1, figsize=(12, 10),
                         gridspec_kw={"height_ratios": [1.5, 1.0],
                                      "hspace": 0.4})
bp.annotated_series(axes[0], series, events=key_events, colors=colors,
                    ylabel="Price (% of par), London",
                    title="Chinese sterling bonds in London, 1885-1929")

# service-probability bands for the two workhorse secured loans
b1896 = pr.prob_bands(series["5% Gold 1896"], consols, 0.05,
                      maturity_years=30, recoveries=(0.25, 0.5, 0.75))
breorg = pr.prob_bands(series["5% Reorganisation 1913"], consols, 0.05,
                       maturity_years=45, recoveries=(0.25, 0.5, 0.75))
ax = axes[1]
bp.prob_band(ax, b1896, "recovery_50pct",
             "5% Gold 1896 (customs-secured)", color=colors["5% Gold 1896"])
bp.prob_band(ax, breorg, "recovery_50pct",
             "5% Reorganisation 1913 (salt-secured)",
             color=colors["5% Reorganisation 1913"])
bp.mark_events(ax, key_events, numbered=False)
ax.set_ylabel("Implied P(full service)")
ax.set_title("Implied probability that the revenue pledge keeps paying",
             fontsize=10)
ax.legend(loc="lower left")
save_fig(fig, "china_probabilities",
         footnote="Two-state model against UK consols. Line: 50% recovery "
                  "on failure; shading spans 25-75% (secured debt rarely "
                  "went to zero).\n" + bp.event_key(key_events))

# ------------------------------------------------------ event studies ----
qing = series["5% Gold 1896"].loc[:"1912-12-31"]
rep = series["5% Reorganisation 1913"]

moves_q = es.largest_moves(qing, k=10)
save_table(es.match_events(moves_q, events, tolerance_days=45),
           "china_qing_largest_moves")
print(f"Qing chance-match baseline: "
      f"{es.chance_match_rate(qing, events, 45):.0%}")
moves_r = es.largest_moves(rep, k=10)
save_table(es.match_events(moves_r, events, tolerance_days=45),
           "china_republic_largest_moves")
print(f"Republic chance-match baseline: "
      f"{es.chance_match_rate(rep, events, 45):.0%}")

car_q = es.event_window_study(
    qing, events[(events.major == 1) & (events.date < "1913")],
    pre=1, post=2, benchmark=None)
save_table(car_q.set_index("event"), "china_qing_event_windows")
car_r = es.event_window_study(
    rep, events[(events.major == 1) & (events.date >= "1913")],
    pre=1, post=2, benchmark=None)
save_table(car_r.set_index("event"), "china_republic_event_windows")

# --------------------------------------------------------- narrative ----
print("\n5% Gold 1896, key levels:")
for label, d in [("pre-Boxer (May 1900)", "1900-05-31"),
                 ("Boxer siege (Jul 1900)", "1900-07-31"),
                 ("after relief (Sep 1900)", "1900-09-30"),
                 ("eve of revolution (Sep 1911)", "1911-09-30"),
                 ("revolution (Dec 1911)", "1911-12-31"),
                 ("republic (Jun 1912)", "1912-06-30")]:
    s = series["5% Gold 1896"]
    if d in s.index.strftime("%Y-%m-%d").tolist():
        print(f"  {label}: {s.loc[d]:.1f}")
print("\n5% Reorganisation 1913, key levels:")
for label, d in [("issue (Jul 1913)", "1913-07-31"),
                 ("Yuan dies (Jun 1916)", "1916-06-30"),
                 ("warlord wars (Oct 1924)", "1924-10-31"),
                 ("May Thirtieth (Jun 1925)", "1925-06-30"),
                 ("Northern Expedition (Dec 1926)", "1926-12-31"),
                 ("Nanking decade opens (Jun 1928)", "1928-06-30"),
                 ("end of sample (Dec 1929)", "1929-12-31")]:
    if d in rep.index.strftime("%Y-%m-%d").tolist():
        print(f"  {label}: {rep.loc[d]:.1f}")
t = series["8% Treasury notes 1920s"]
print(f"\n8% Treasury notes (unsecured): {t.iloc[0]:.0f} ({t.index[0]:%b %Y})"
      f" -> min {t.min():.0f} -> {t.iloc[-1]:.0f} ({t.index[-1]:%b %Y})"
      f"  [defaulted; contrast with the secured loans above]")
