# Bond Markets as War-Outcome Prediction Markets: Findings

*Companion to [RESEARCH_PLAN.md](RESEARCH_PLAN.md). Every number below is
reproducible: `pip install -r requirements.txt`, `bash scripts/fetch_data.sh`,
`python scripts/prepare_data.py`, then `python analysis/0X_*.py`. Figures and
tables cited are in `output/`.*

## 1. The mechanism in one paragraph

A belligerent's bond bundles two bets: on world interest rates and on the
issuer's survival. On a *neutral* exchange (Amsterdam 1863, London 1914,
Zurich 1940) the second bet dominates, and the price decomposes as
`P = π·V_win + (1−π)·V_lose`, where `V_win` is the bond's value if the issuer
wins (its promised cash flows discounted at the neutral market's risk-free
yield — UK consols here) and `V_lose` its recovery under defeat. Inverting
gives the market-implied victory probability `π = (P − V_lose)/(V_win −
V_lose)`. Since `V_lose` is not observable ex ante, we report **bands** over
recovery assumptions rather than a single line. Where the level of `π` is too
assumption-sensitive, the **changes** remain informative, so each war also
gets a Willard–Guinnane–Rosen-style event study: rank the largest market
moves, then ask what news arrived; and compute cumulative returns around the
named battles with a z-score against ordinary wartime volatility.

Validation: our implementation reproduces Weidenmier & Oosterlinck's (2007)
headline number — at the pre-Gettysburg price of 60, the model yields a
**42.9%** implied probability of Confederate victory against their ~42%.

**Identification discipline.** Event attributions on monthly data are easy to
overclaim, so the pipeline enforces four rules. (i) *No look-ahead*: a large
move is only ever matched to an event **at or before** the quote date — a
month-end price cannot react to next week's news. (ii) *A placebo base rate*:
each largest-moves table is published alongside the **chance-match rate** —
the share of *all* observation months that would match some chronology event
under the same rule (30–52% here, the chronologies being dense). Matches are
informative only insofar as they beat that base rate in timing specificity
and sign-consistency, not because a match exists. (iii) *An estimation
window*: event-window z-scores are computed against volatility estimated
from the **non-event months only**, as in a standard event study — full-sample
sigma would let the event shocks inflate the null and shrink every z.
Windows of nearby events can share months; the tables flag these overlaps
(`overlaps`), which are joint, not independent, tests. (iv) *Clipping is
reported, not hidden*: wherever the two-state inversion pins π at 0 or 1
(price outside the assumed [V_lose, V_win]), the share of clipped months is
printed — where it is large, only *changes* in π are interpretable, not
levels. None of this makes the exercise causal in the potential-outcomes
sense: with one price path per war there is no counterfactual, and the design
is an *event study on archival data*, i.e. descriptive evidence that markets
aggregated war news, subject to the selection caveats in §13.

## 2. US Civil War, 1861–65 (full treatment)

**Instruments.** Union: the gold value of $100 in greenbacks, New York gold
room, monthly averages of daily quotes 1862–65 (Mitchell 1908, Table 2, parsed
from the public-domain scan with a reciprocal-identity cross-check). The
greenback was a claim on eventual resumption, which contemporaries tied to
Union victory at bearable fiscal cost. Confederacy: the CSA 8% gold bonds
traded in Amsterdam (monthly series anchored to Weidenmier–Oosterlinck's text
and Figure 1; see `data/manual/PROVENANCE.md`).

**Probability paths** (`output/civilwar_probabilities.png`). The two sides'
implied probabilities are strikingly *not* mirror images — informative because
they come from different markets pricing different instruments:

- Union-victory-with-resumption probability starts near 1.0 in early 1862,
  breaks on the Seven Days and the Legal Tender inflation (0.75 by late 1862),
  recovers with Gettysburg/Vicksburg (July 1863: 0.62 → 0.83 in the central
  scenario), then collapses through Grant's bloody, stalled 1864 summer to its
  war-time floor in July–August 1864 (greenbacks at 38.7 cents gold — under a
  40-cent defeat-recovery assumption the implied probability touches **zero**).
  This is exactly the moment Lincoln himself wrote he expected to lose the
  election. Atlanta (Sept 1864, +14%) turns it; the largest monthly gains of
  the war come at its end — +18.1% in March 1865 as final victory was priced
  in ahead of Richmond's fall (the month's chronology match is McCulloch's
  Treasury nomination; Sherman's Carolinas march is the likelier driver), and
  +17.0% in April (Richmond and Appomattox).
- Confederate victory probability starts at ~0.43 pre-Gettysburg, drops to
  ~0.25 by end-1863, decays through 1864 with only two blips (Chickamauga
  +/−, and the July 1864 Wilderness/Early rally: 0.07 → 0.11), and is under
  2% by January 1865. Consistent with Weidenmier–Oosterlinck, the market
  never believed the 1864 peace-platform scenario.

**Turning points** (`output/civilwar_greenback_largest_moves.csv`, event
windows in `..._event_windows.csv`; chance-match base rate 52%): the largest
greenback moves match, in order of size: Early at Washington + the gold
corner (Jul 1864, −18.5%), the end-of-war repricing (Mar 1865 +18.1%, Apr
1865 +17.0%), Atlanta (+14.0%), Gettysburg/Vicksburg (+10.7%), the Legal
Tender Acts (Jan–Feb 1863, −8.9% each). Note how *financial* legislation
rivals battles — greenbacks priced fiscal credibility jointly with military
survival.

## 3. World War I, 1914–18 (full treatment; the Brusilov test case)

**Instruments.** London monthly quotes (Yale ICF *Investor's Monthly Manual*):
Russia 5% 1906 (the empire's flagship external loan), France 3% rentes,
Germany Imperial 3% 1891–3, Austria 4% gold rentes; benchmark UK consol
yields (NBER m13041c). Caveats: minimum-price rules in London early in the
war and thin enemy-issuer trading mean levels are cleanest for Russia and
France; German/Austrian series are still informative directionally.

**The Brusilov Offensive** — the motivating example — is clearly visible
(`output/ww1_russia_closeup.png`): the Russian 5% 1906 jumped from 83.9 (May
1916) to 90.0 (June 1916), **+7.3%, the second-largest monthly gain of
Russia's war**, as the offensive collapsed the Austrian front; it held ~90
through September (implied survival probability 66% → 69–70%), then gave the
gain back by November as the offensive stalled and Romania's entry turned
into a liability (Bucharest fell in December; −7.3%). So: yes, a single
campaign moved the market's estimate of Russia's survival by ~4–7 percentage
points — but the market also *marked the gain back down* when the strategic
picture reverted, which is what a functioning prediction market should do.

**Russia's full turning-point ranking** (`output/ww1_russia_largest_moves.csv`;
chance-match base rate 42%) is dominated not by battles but by **regime and
exit events**: October Revolution (−13.5%), the Brest-Litovsk armistice
(−8.7%), war outbreak (−8.8%), Brusilov (+7.3%), the November 1916 slide
(−7.3%, Bucharest fell in early December — under the no-look-ahead rule the
move stays unattributed), and the January 1918 slide (−7.6%) as repudiation
loomed (the decree itself came days after the quote). And then, remarkably,
the bond *rallies double digits* in mid-1918 (+11.4% in June — unattributed;
+8.2% July, matched to the Second Marne; +11.2% October, after Bulgaria's
armistice) as the Central Powers collapsed: by late 1918 London priced a
meaningful chance the repudiation would not stand (see §4).

**Cross-country read.** France's rentes never priced serious defeat risk
after the Marne (survival probability stays 0.75–0.85); Austria's gold
rentes fall first and furthest of the majors during Brusilov (its implied
survival dips toward 0.35–0.40 in mid-1916, the lowest of any belligerent
until 1917) — the market correctly identified Austria-Hungary as the
weakest link years before the end.

## 4. Russian Civil War, 1917–22 (full treatment)

Same instrument, new question: after February 1918 the repudiated Tsarist 5%
1906 is a pure bet on *the repudiation being undone* — White victory, Soviet
collapse, or an enforced settlement. Findings
(`output/rcw_probabilities.png`, `output/rcw_largest_moves.csv`):

- The implied probability of a debt-honoring outcome was still **~39% at the
  repudiation** (price 48.5) — the market treated the Bolsheviks as likely
  transient — and **~46% in June 1919** at Denikin's peak advance.
- The White high-water mark of October 1919 (Orel, Yudenich at Petrograd)
  shows prices *already sliding* (43.5, ~36%): London was marking the Whites
  down even as they stood closest to Moscow — Kolchak's simultaneous Siberian
  collapse and Britain's waning commitment dominated.
- The definitive de-rating comes in 1920: Denikin's Novorossiysk disaster
  (27%), then Wrangel's Crimean evacuation (**14%**, price 20.5). The
  largest single moves of the sub-period are the Soviet-Polish war swings
  (April–May 1920 −18/−24%, September 1920 −20% after Warsaw ended
  intervention hopes).
- A long, fat tail of "hope springs eternal" (Landon-Lane & Oosterlinck):
  prices of 8–15 persist through 1923, spiking +52% in Dec 1921 and +18.5%
  around Genoa/Rapallo (Apr 1922) on settlement rumors — a **peso problem**:
  the level overstates White victory odds because it bundles in
  bailout/settlement scenarios. This is why we report the RCW π as
  "probability the repudiation is undone", not "White military victory".

## 5. World War II, 1933–48 (full treatment)

**Instruments.** Frey & Waldenström's monthly Zurich prices for German,
French and Belgian state bonds (plus Stockholm for Germany/Belgium),
1933–48. Germany was already in partial external default after 1933, so
V_win is anchored to the 1936–38 trading level rather than par, and the
German series must be read knowing Swiss–German clearing politics supported
prices into 1944 (the "Zurich puzzle" in the literature). That anchor is
visibly too low for 1940–42: German prices sat *above* it and the inversion
clips π at 1.0 in **33% of war months** (France 18%, Belgium 0%) — so the
German *level* is uninformative there, and only its collapses and recoveries
should be read.

**German bonds as an Axis-victory barometer**
(`output/ww2_germany_largest_moves.csv`, `..._event_windows.csv`):

| Event | Market reaction (Zurich) |
|---|---|
| Czech crisis, Aug 1938 | −16.4% |
| Schacht dismissed, Jan 1939 | −19.5% |
| **War begins, Sep 1939** | **−48.2%, the largest move of the sample** (window CAR −47.7%, z = −5.1 vs non-event volatility) |
| Fall of France, Jun–Jul 1940 | **+50.0%** (event-window CAR +67%, z = 4.1) |
| Stalingrad/Feb 1943 | trend break: survival index slides from ~1.0 (1942) to 0.6–0.75 (1943–44) |
| Ardennes failure + Yalta, Dec 44–Feb 45 | −43.3%, window CAR −46% (z = −4.9) |

The market's most violent updates were the *outbreak of the war itself*
(priced as a disaster for Germany's creditors) and the *fall of France*
(priced as near-victory). Mid-war attrition news moved Zurich far less than
these regime-scale shocks — partly rational (the bonds' fate hinged on total
victory vs. total defeat, not on battles per se), partly institutional
(clearing-agreement support).

**Occupied countries.** Belgian and French bonds in Zurich crash on
occupation-finance events (Jan–Feb 1941: France −60%, Belgium −54%, when
transfer moratoria bit), then **rally on Allied fortunes** — Belgium +18.3%
in the month of Stalingrad's surrender, France +25.6% in the month of
D-Day/Bagration — a clean mirror-image confirmation that these prices carried
outcome information, not just cash-flow mechanics.

## 6. Vietnam War (documented negative result)

No instrument exists (`output/vietnam_data_availability.csv`): South Vietnam
was financed by US aid, not marketable debt (and its domestic piastre bonds
had no neutral quotation); North Vietnam borrowed from the USSR/China; US
Treasuries never priced US *solvency* as a function of the war. The closest
historical instrument — French Indochinese bonds in Paris — priced the
First Indochina War (to 1954) under a metropolitan guarantee. **This is
itself a finding about the mechanism's scope: it requires a belligerent whose
debt service hinges on the war's outcome and which funds itself through
markets.** Cold-war client states funded by superpower aid fail both legs.

## 7. Iran–Iraq War (documented negative result)

Same failure mode, starker (`output/iran_iraq_data_availability.csv`,
following Hinrichsen 2019): Iraq entered the war a net *creditor* and
financed it with Gulf-state deposits/loans, export credits and military
credits — none traded; quotations for Iraqi claims first appear after the
1990 Kuwait invasion at cents on the dollar. Revolutionary Iran repudiated
foreign borrowing and financed the war from oil. The 1980s secondary market
for LDC bank loans carried no regular Iran/Iraq quotes during the war.
War-sensitive prices that *did* exist (tanker war-risk insurance premia, oil
futures) price supply disruption, not either side's victory probability.

## 8. Denmark and the war of 1864 (hand-collected London bargains)

`analysis/07_schleswig_1864.py`; data hand-read from page scans of *The
Economist*'s Bankers' Price Current (`data/manual/danish_london_1862_1865.csv`,
method in `scripts/fetch_danish_pages.py` and PROVENANCE.md), predating the
IMM's 1869 start.

Denmark's three London loans — the 3% of 1825, the 4% of 1863 and the 5%
war loan Hambro floated for £1.2m in January 1864, *while the Austro-
Prussian ultimatum was running* — price the crisis as fiscal damage, never
as default risk. The 3% 1825 slid from 84 (mid-Dec 1863, federal execution
imminent) to 81½–82 as the ultimatum expired, marked nothing at all through
the invasion, reappeared at 78 while the London Conference sat, and
bottomed at 74 in the days after the peace preliminaries ceded two-fifths
of the monarchy — a peak-to-trough of ~12%, a yield spread over consols
that only widened from 33bp to 68bp, and an implied P(full service) that
never fell below ~2/3 under even a harsh 50%-recovery assumption. By March
1865 it stood at 80½. The war loan itself tells the sharpest story: 93.4
during the armistice, **95.5 on 17 June 1864 as the market bet the London
Conference would hold, −5% to 90¾ xd once the war resumed and Als fell**,
then a steady climb to 98 by March 1865 (and par by 1869 in the IMM).

The methodological finding is as important: **in most crisis weeks London
marked no Danish bargains at all** — of ~82 issues examined, only 23
contain any Danish business, and none of the older bonds traded between
23 Jan and 21 May 1864 (the invasion, the Dannevirke retreat, Dybbøl).
Small-power debt in a great-power crisis went *illiquid before it went
cheap*; a monthly "probability path" interpolated through that silence
would be an artifact. This is why the Danish study reports levels,
between-bargain moves and bounds instead of a π line.

## 9. Franco-Prussian War, 1870–71 (both sides' debt survived)

`analysis/08_franco_prussian.py`, IMM monthly quotes from 1869.

France serviced the rentes through defeat, siege, Commune and the 5bn-franc
indemnity, so the priced event is the *burden of losing*, not repudiation.
The 3% rente fell from 74.6 (May 1870) to 53 by November — −27%, with the
three largest monthly moves stacked on the outbreak (−8.8%), Gravelotte/
Metz (−8.2%) and Sedan/the siege (−9.5%); the war-outbreak event window
carries a CAR of −24% (z ≈ −11). London then marked no rente bargains at
all from January to March 1871 (siege and Commune — the same illiquidity
signature as Copenhagen's bonds in 1864). Recovery came not with Frankfurt
but with the *fiscal* resolution: +3.4% when the Commune fell, +4.3%
around the first oversubscribed Thiers rente, back to pre-war-minus-a-
quarter by the time the indemnity was prepaid in Sept 1873.

The German side is a control experiment. The North German Confederation's
5% war loan of 1870 — floated in London mid-war — never traded below 98,
and the NBER German bond-yield series peaks at 4.71% in July 1870 and
*falls* through the war to 4.48%. London also absorbed the French 6%
"Morgan" loan of Oct 1870 (a belligerent borrowing abroad mid-war, like
Denmark 1864 and the Confederacy 1863): issued into the siege at ~84, it
reached par within a year. Asymmetric warfare, symmetric conclusion: the
market read this war correctly and almost immediately — Sedan is the
regime break, everything after is fiscal arithmetic.

## 10. China, 1885–1929 (the pledge outlives the dynasty)

`analysis/09_china.py`. China's sterling loans were secured on specific
revenues (Imperial Maritime Customs; salt) collected under foreign
supervision, so the priced event is the survival of that *revenue
machinery*, not of the Qing. The market's rankings bear this out:

- **The Boxer summer of 1900 is the largest Qing-era shock**: the
  customs-secured 5% 1896 fell 95 → 78.5 (−12.8% in July alone, the
  biggest monthly move of the dynasty's sample) — precisely because the
  legation siege threatened the foreign-run customs itself — and
  recovered half the loss within two months of the relief.
- **The 1911 revolution barely registered**: 104 (Sept 1911) → 101.5
  (Dec) → 101 (June 1912). The dynasty fell; the customs kept collecting;
  the bonds shrugged. The market correctly treated Shimonoseki (1895),
  which forced the indemnity borrowing, as worse news than Wuchang.
- **The Republic priced as a slow institutional decay**: the salt-secured
  5% Reorganisation Loan of 1913 traded ~90 at issue, 79 when Yuan Shikai
  died, 72 through the second Zhili–Fengtian war, 69 after May Thirtieth,
  and 55 at the Northern Expedition's height (Dec 1926), recovering to
  ~62–64 as Nanking consolidated and began rehabilitating foreign-debt
  service. No single battle dominates: the warlord decade shows up as a
  drift with 7–9% monthly swings at the chance-match baseline, i.e. the
  market priced cumulative institutional erosion, not campaigns.
- **The unsecured tier shows what security was worth**: the 8% sterling
  Treasury notes of 1919-20 went 99 → 14 and stayed there (default),
  while the secured loans of the same government never broke 46.

## 11. The Ottoman decline, 1869–1929 (sixty years, one narrative)

`analysis/10_ottoman.py`. Five series spanning three regimes: the
unsecured 5% General Debt of 1865, the customs-secured 6% of 1858, the
Anglo-French-guaranteed 4% of 1855, the post-restructuring Converted
(Muharrem) series, and the 4% Unified Debt.

- **The market called the 1875 default years ahead.** The unsecured
  General Debt yielded ~9–10% already in 1869–73 (implied P(full service)
  never above ~35% under a 15%-recovery assumption), lurched −28% when
  the Franco-Prussian war removed Paris as the Porte's lender of last
  resort, and drifted from 54 (1872) to 35 before the Ramazan decree
  (−26% in Oct 1875) made it official.
- **The collateral decomposition identifies what was feared**: from calm
  (June 1872) to the war's depth (Dec 1877), unsecured 54→8.5, customs-
  secured 71→9, guaranteed 102→103. Bondholders feared Ottoman fiscal
  collapse, not the geopolitical extinction the guarantee insured
  against; when the Russians reached San Stefano, the guaranteed 4%
  still traded above par.
- **War moves are huge but second to debt-regime moves**: Russia's
  declaration (−39%, Apr 1877) and the deposition summer of 1876 (−21%,
  +24%) are the largest war-driven swings; the Congress of Berlin
  (+15.5 → 28 on the customs bond within a month) and the Muharrem decree
  restored more value than any battle destroyed. After Muharrem the OPDA
  series traded on administration, not armies: the 1897 Greek war, won
  handily, is barely visible.
- **The Unified Debt's last two decades read as an obituary**: 96 before
  the Young Turk revolution, −4 on the revolution itself, 88 through the
  Libyan war, 85 through the First Balkan War (Çatalca held), 78 on the
  entry into WWI, 52 at the last free London quote (July 1916), a
  Mudros/armistice bounce to 66 (creditors preferred a partitioned debtor
  under Allied control), then 20 at Lausanne — apportionment among
  successor states with service suspended — and only 24.5 even on the
  1928 Paris agreement. The empire's debt outlived the empire by a
  decade, at a fifth of face.

## 12. Cross-war conclusions

1. **The mechanism works where its preconditions hold** (traded debt on a
   neutral exchange, outcome-contingent repayment): the Civil War, WW1,
   the Russian Civil War and WW2 all yield probability paths whose major
   inflections coincide with the events military historians independently
   flag as decisive — Gettysburg/Vicksburg, Atlanta, Brusilov, the October
   Revolution, the fall of France, Stalingrad.
2. **Markets updated on strategic shocks, not tactical drama.** Regime
   events (revolutions, repudiations, great-power entries/exits, the
   outbreak of war itself) move prices 2–5× more than famous battles.
   Battles matter most when they resolve *strategic* uncertainty (Gettysburg
   + Vicksburg together; France 1940; Stalingrad as trend break).
3. **Levels are assumption-laden; changes are robust.** π depends on
   recovery and discounting assumptions (hence bands), and peso problems
   (Russia post-1918, the Zurich clearing puzzle) can hold prices above
   "pure victory odds". The event-study layer is the assumption-light
   complement.
4. **The mechanism has a clear historical domain.** It spans conflicts
   fought by market-financed states — roughly 1850s–1945 at its best — and
   fails for aid-financed Cold-War conflicts (Vietnam) and state/bank-
   financed 1980s wars (Iran–Iraq). For post-1990 wars it works again via
   secondary bond markets and CDS (e.g. Ukraine 2022 bond pricing), which is
   the natural extension of this project.
5. **What exactly is priced is identified by the debt's structure, not by
   the analyst.** The extension cases make this observable directly:
   Ottoman collateral tiers (guaranteed flat above par, secured −87%,
   unsecured −85% with lower recovery) show 1875–78 was priced as fiscal
   collapse, not state extinction; China's customs-secured loans sailing
   through the 1911 revolution while unsecured Treasury notes went to 14
   show the market pricing *revenue machinery*, not dynasties; France
   1870–73 and Denmark 1864 show defeat priced as a burden (a level shift
   in yield) where repudiation was never in question.
6. **Illiquidity is a war signal in its own right.** The two hand-collected
   panics — London's Danish book in Feb–Apr 1864 and its rente book in
   Jan–Mar 1871 — both show the market going *silent* precisely at maximum
   uncertainty. Thin-market silence bounds what any probability path can
   claim at exactly the moments a naive reading would call most
   informative.
7. **Belligerents could borrow *into* the crisis, and the price of the new
   paper is a clean prediction-market read.** Denmark's January 1864 war
   loan (issued at 93 under an active ultimatum, 95.5 while the peace
   conference sat, 98 within months of losing) and France's October 1870
   Morgan loan (issued into the siege at ~84, par within a year) both
   measure the market's estimate of the *post-war state's* solvency, free
   of legacy-coupon complications.

## 13. Limitations

- Monthly frequency (data-limited) smears event timing by up to a month;
  the "candidate event" matching is suggestive, not causal identification.
  The chance-match base rates (30–52%) quantify how much of that matching
  could arise mechanically; the event chronologies were also compiled
  knowing how the wars ended, an unavoidable hindsight-selection risk.
- Event-window z-scores use non-event volatility as the null, but nearby
  events share window months (flagged `overlaps` in the tables): clustered
  windows are one joint test, not several independent ones, and no
  multiple-testing correction is applied across the ~15–20 events per war.
- The two-state inversion clips π to [0, 1]; the published clipping shares
  (e.g. 33% of German war months in WW2, 17% of greenback months) mark the
  stretches where the level is model-inconsistent and only changes carry
  information.
- The Confederate Amsterdam series is literature-anchored (±2 gold dollars
  on figure-read months); the greenback series is OCR-parsed from the
  public-domain primary compilation with a reciprocal cross-check.
- Wartime market microstructure (minimum prices, moratoria, capital
  controls, censorship) contaminates levels, especially 1914–15 London and
  1940s Zurich; we flag rather than model these.
- Risk-neutrality is assumed throughout; wartime risk premia likely bias
  implied probabilities downward for the side whose defeat correlates with
  investors' broader wealth.
