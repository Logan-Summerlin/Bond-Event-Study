# Research Plan: Bond Markets as War-Outcome Prediction Markets

**Goal.** For ten conflicts — the US Civil War, World War I, the Russian Civil
War, World War II, the Vietnam War, the Iran–Iraq War, and four extension
cases (Denmark's war of 1864, the Franco-Prussian War, Chinese debt under the
Qing and the Republic, and the Ottoman decline) — use the market pricing of
the belligerents' sovereign debt (traded, wherever possible, on *neutral*
exchanges) to (a) estimate the market-implied probability that each side would
win — or, where the debt survived defeat, that it would be serviced in full —
and (b) where a full probability model is not defensible, run event studies
identifying the battles, campaigns, and political shocks that most moved market
opinion about the war's outcome.

---

## 1. Theoretical framework

### 1.1 Why sovereign bond prices encode war odds

A government bond promises fixed cash flows. Its price is the discounted
expected value of those cash flows, and the expectation is taken over states of
the world. In wartime, the dominant state variable for a belligerent's debt is
**who wins**:

- If the issuer **wins**, its debt is (usually) honored: the bond is worth its
  "peace value" `V_W` — roughly the price of a comparable bond of an undefeated,
  solvent sovereign.
- If the issuer **loses**, its debt is impaired: repudiation (Soviet Russia
  1918, North Vietnam's treatment of South Vietnamese/colonial obligations),
  currency destruction (the Confederacy, Weimar's inflation of WWI domestic
  debt), or partial haircut/rescheduling. Call this recovery value `V_L`.

With risk-neutral pricing, the observed price is

```
P_t = π_t · V_W(t) + (1 − π_t) · V_L(t)
⇒  π_t = (P_t − V_L) / (V_W − V_L)          (the "two-state model")
```

where `π_t` is the market-implied probability of victory (more precisely, of
*debt survival*, which bundles victory with a negotiated peace that honors the
debt). This is exactly the mechanism used in the academic literature this plan
builds on:

- Willard, Guinnane & Rosen (AER 1996), *Turning Points in the Civil War* —
  the gold price of greenbacks as a Union-victory/resumption probability.
- Weidenmier (2000, 2002); Oosterlinck & Weidenmier (NBER wp 13567), *Victory
  or Repudiation* — Confederate cotton-bond prices in Amsterdam/London.
- Frey & Kucher (JEH 2000); Frey & Waldenström (FHR 2004, EEH 2008) — WWII
  belligerent/occupied-country bonds priced in neutral Zurich and Stockholm.
- Oosterlinck (2003+), *Hope Springs Eternal* — repudiated Russian bonds in
  Paris during the Russian Civil War pricing White victory / Soviet reversal.
- Collet & Oosterlinck — French/Indochinese and Vietnamese obligations around
  decolonization and the Vietnam War.

### 1.2 Practical complications the analysis must respect

1. **Recovery is not zero and not known.** `π_t` is identified only up to
   assumptions about `V_W` and `V_L`. We will report probability *bands* under
   several recovery assumptions (e.g. `V_L/V_W ∈ {0, 0.25, 0.5}`) rather than a
   false-precision single line.
2. **Discounting and coupons.** Long-dated bonds' peace value moves with the
   general level of interest rates; we normalize by a neutral risk-free
   benchmark (UK consols, Swiss Confederation bonds, US Treasuries) so that
   `π_t` reflects *relative* default risk, not world rates.
3. **Belligerent home markets are distorted** (price floors, patriotic
   pressure, capital controls, closed exchanges — e.g. London/NYSE closures in
   1914). Neutral-market quotes (Amsterdam, Zurich, Stockholm, Geneva; London
   for non-Entente issuers pre-1917; New York gold room) are preferred.
4. **"Victory" vs "debt survival."** The event actually priced is repayment.
   For the Union greenback, the priced event is resumption of gold
   convertibility; for Tsarist bonds after 1917, it is overthrow/settlement by
   the Soviets. Interpretation sections will be explicit about this mapping.
5. **Peso problems and illiquidity.** Thin wartime markets gap; monthly data
   smooths but also blurs event timing. Event studies will use the highest
   frequency available per war (daily for the greenback market, weekly/monthly
   elsewhere).

### 1.3 Event-study methodology (when the two-state model is too heroic)

Following Willard–Guinnane–Rosen and Frey–Waldenström:

1. Compute log returns (or yield changes) of each belligerent's bond series.
2. **Largest-move ranking:** identify the K largest absolute moves (and largest
   cumulative moves over 1–3 period windows) and match them against a
   hand-compiled chronology of battles, campaigns, and political events.
3. **Structural breaks:** endogenous break detection (binary segmentation /
   Bai–Perron-style via the `ruptures` package) on the price level and on
   return volatility, again matched to the chronology.
4. **Event windows:** for the major named battles/campaigns per war (e.g.
   Gettysburg/Vicksburg, the Brusilov Offensive, Stalingrad, the Tet
   Offensive, al-Faw 1986), compute abnormal returns relative to a neutral
   benchmark over pre/post windows and test significance against the series'
   own wartime volatility.

The two approaches are complements: the two-state model gives a *level*
(probability path), the event study gives *changes* (which news moved the
path).

---

## 2. War-by-war data strategy

Feasibility was verified against live sources before writing this plan. Wars
are tiered by data quality.

### Tier 1 — downloadable market data, full treatment (probability paths + event studies)

**(A) US Civil War, 1861–65**
- *Union:* the gold price of greenbacks (New York gold room), daily/monthly,
  from public-domain compilations (Mitchell 1908; NBER Macrohistory ch. 4/13
  where available). Greenback gold value ≈ probability-weighted resumption
  claim ⇒ Union-victory probability via the two-state model.
- *Confederacy:* the 7% Erlanger cotton loan traded in Amsterdam/London
  (Weidenmier 2000; Oosterlinck & Weidenmier 2007). If no machine-readable
  series is downloadable, digitize the monthly series from the published
  papers, labeled as literature-derived.
- Chronology: Bull Run, Antietam, Emancipation, Gettysburg+Vicksburg,
  Chickamauga, Atlanta, Lincoln's re-election, Appomattox, plus the financial
  events (Legal Tender Acts, gold corner of 1864).

**(B) World War I, 1914–18**
- Yale ICF *Investor's Monthly Manual* (London Stock Exchange, monthly,
  1869–1930, free CSV): Russian 4%/5% state bonds, French rentes, Japanese,
  Italian, and (pre-war and where quoted) German/Austrian issues.
- NBER Macrohistory: UK consol yields (m13041b/c, spliced 1852–1938),
  German bond yields (m13028a, 1870–1913).
- Focus case per the user's example: **Russian Imperial bonds through 1914–17**
  (Tannenberg, Gorlice–Tarnów, the Brusilov Offensive June–Sept 1916, the
  February and October Revolutions), measuring how much each campaign moved
  Russia's implied survival probability.
- Caveat to be documented: wartime London applied minimum-price rules early in
  the war; cross-checks against post-1915 data and known literature results.

**(C) Russian Civil War, 1917–22**
- Same IMM London quotes of repudiated Tsarist bonds after February/October
  1917 and the February 1918 repudiation decree. Price ≈ probability of
  White victory (or Soviet settlement) × expected recovery. Event study against
  Kolchak's and Denikin's 1919 offensives, Yudenich at Petrograd, the Polish
  war, Wrangel's evacuation.

**(D) World War II, 1933/39–45**
- Frey & Waldenström monthly bond prices, **Zurich and Stockholm exchanges,
  1933–1948** (publicly posted by Waldenström, verified): Germany, France,
  Belgium, Denmark, Norway, Finland, plus neutral benchmarks (Switzerland,
  Sweden). Implied survival probabilities for Germany and the occupied states;
  event studies around Munich, fall of France, Barbarossa, Stalingrad,
  Normandy, etc.

### Tier 2 — no freely downloadable series located; literature-derived series + event study

**(E) Vietnam War, 1955–75**
- Peer-reviewed source series: Paris-traded Indochinese/South-Vietnamese
  obligations (Oosterlinck & Collet line of work) and any South Vietnamese
  domestic issues documented in the literature. If only figures/tables in
  papers are available, digitize monthly values with explicit provenance
  labels; event study around Dien Bien Phu (predecessor conflict), Tet 1968,
  the Easter Offensive 1972, the Paris Accords, and the 1975 collapse.
- Fallback if no defensible series can be constructed: a documented
  data-availability analysis explaining *why* the mechanism fails here
  (US-guaranteed financing, aid-driven solvency, thin markets), which is
  itself a research finding.

### Extension cases (added after the first six wars)

**(G) Denmark and the Schleswig-Holstein crisis, 1863–65**
- Pre-dates the IMM (1869), so no machine-readable London series exists.
  Primary source: *The Economist*'s weekly "Bankers' Price Current —
  Prices of Foreign Stocks" table, public-domain page scans on archive.org
  (Serials-in-Microfilm). Table OCR is unusable; the pipeline
  (`scripts/fetch_danish_pages.py` + `..._hocr.py`) locates the price-
  current leaf per issue via hOCR word coordinates and saves cropped
  strips, from which every Danish bargain 1862–65 was read by eye into
  `data/manual/danish_london_1862_1865.csv`.
- Instruments: Danish 3% 1825, 4% 1863, and the 5% war loan Hambro
  floated in London in January 1864. Benchmark: UK 3% consols (NBER
  m13041b, monthly from 1852).
- Design constraint discovered in the source: quotes are *marked
  bargains*, absent in most weeks (including the whole invasion phase),
  so the analysis reports levels, between-bargain moves and probability
  bounds — not an interpolated monthly π line.

**(H) Franco-Prussian War, 1870–71**
- IMM London quotes from 1869 cover the war: French 3% rentes
  (continuous, with a documented quote suspension Jan–Mar 1871), the
  French 6% "Morgan" sterling loan of Oct 1870, and the North German
  Confederation's 5% war loan of 1870; NBER m13028a supplies German
  bond yields monthly from Jan 1870.
- Both sides' debt survived (France serviced the rentes throughout), so
  π is read as P(full service) and interpreted as a *war-burden
  discount*; the event study on rente changes is the primary output.

**(I) China under the Qing and the Republic, 1877–1929**
- IMM London quotes: early loans (8% 1874–6, 8% 1877, 7% Series A), the
  indemnity loans of 1895/1896/1898, railway loans (incl. Hukuang 1911),
  the 5% Reorganisation Loan 1913, and the (defaulted) 8% sterling
  Treasury notes of 1919–20.
- Chinese external debt was secured on foreign-supervised revenues
  (Maritime Customs, salt), so the priced event is the survival of the
  revenue machinery: the design compares secured vs unsecured issues and
  reads π as P(full service) with recovery bands reflecting security.
- Chronology: Sino-French and Sino-Japanese wars, Shimonoseki indemnity,
  concession scramble, Boxer summer 1900 and Protocol, the 1911
  revolution, the Reorganisation Loan, the Twenty-One Demands, the
  warlord wars, May Thirtieth, the Northern Expedition, Nanking.

**(J) The Ottoman decline, 1869–1929**
- IMM London quotes across three debt regimes: pre-default issues
  spliced as the unsecured 5% General Debt 1865, the customs-secured 6%
  1858 and the Anglo-French-guaranteed 4% 1855 (a built-in placebo:
  guaranteed paper should not move on Ottoman news); the post-Muharrem
  Converted Series A/B (OPDA); the 4% Unified Debt 1904–29.
- Chronology: the 1875 Ramazan default and 1876 suspension, the Great
  Eastern Crisis and Russo-Turkish war, San Stefano vs Berlin, the 1881
  Muharrem decree/OPDA, the 1897 Greek war, the Young Turk revolution,
  Libya, the Balkan wars, WWI (London quotation ceases mid-1916),
  Mudros, Sèvres, Lausanne, and the 1928 Paris service agreement.

### Tier 3 — mechanism likely infeasible; document why + best proxy

**(F) Iran–Iraq War, 1980–88**
- Neither belligerent had liquid traded sovereign bonds during 1980–88: Iraq
  financed the war with Gulf-state loans and export credits; post-revolution
  Iran largely repudiated external borrowing. The secondary market for
  distressed sovereign *bank loans* (born mid-1980s) carried at most sparse
  Iraqi quotes.
- Plan: (i) search for secondary-market loan quotes (Salomon/Merrill LDC loan
  price sheets, academic compilations); (ii) if unavailable, present the
  negative result rigorously and, as a proxy, examine prices *sensitive to the
  war's outcome* (e.g. war-risk shipping premia or Kuwaiti/Gulf market data)
  only if a real series can be found. No fabricated data.

---

## 3. Implementation architecture

```
Bond-Event-Study/
├── RESEARCH_PLAN.md          # this document
├── REPORT.md                 # findings, figures, interpretation, caveats
├── requirements.txt
├── data/
│   ├── raw/                  # downloaded files, unmodified (+ SOURCES.md)
│   ├── manual/               # hand-entered series from cited publications
│   │   └── PROVENANCE.md     # source, table/figure, method for every series
│   ├── processed/            # cleaned CSVs: date, issuer, market, price/yield
│   └── events/               # per-war chronology CSVs
├── src/bondwar/
│   ├── data_loaders.py       # NBER, IMM, Frey–Waldenström, manual loaders
│   ├── probability.py        # two-state model, recovery-assumption bands
│   ├── event_study.py        # returns, largest moves, breaks, event windows
│   └── plotting.py
├── analysis/                 # one runnable script per war → output/
│   ├── 01_us_civil_war.py … 10_ottoman.py
└── output/                   # figures (png) + tables (csv/md)
```

Python 3, pandas/numpy/matplotlib/scipy (+ `ruptures` for break detection).
Everything reproducible end-to-end: `pip install -r requirements.txt`,
`python analysis/0X_*.py` regenerates outputs from `data/`.

## 4. Deliverables

1. **Probability paths** `π_t` (with recovery-assumption bands) for every
   belligerent series with adequate data: Union, Confederacy, Russia (WWI and
   Civil War), Germany/France/Belgium/etc. (WWII), plus whatever Tier 2/3
   yields.
2. **Event-study tables** per war: top market-moving dates matched to battles/
   campaigns/political events, with magnitude and direction.
3. **Figures**: price/probability series annotated with the chronology.
4. **REPORT.md**: methodology, per-war narrative (did the Brusilov Offensive
   move Russian bonds? what did Zurich "know" after Stalingrad?), cross-war
   comparison of how quickly and correctly markets updated, and honest
   limitations (recovery identification, market microstructure, censorship,
   capital controls, hindsight bias in event selection).

## 5. Known assumptions (flagged for the user)

- **Frequency:** monthly for most wars (that is what survives); daily where
  public-domain (greenback market) — event studies are correspondingly coarser
  elsewhere.
- **Literature-derived data:** where no machine-readable source exists, series
  digitized from published academic tables/figures are used and are always
  labeled as such in `data/manual/PROVENANCE.md`. No synthetic/invented data.
- **"Victory probability" ≡ debt-survival probability** under stated recovery
  assumptions; the report is explicit whenever the two diverge (e.g. a
  negotiated peace).
- Language/stack: Python; all outputs regenerable from the repo.
