# Provenance of hand-entered series

Nothing in this directory is primary machine-readable data. Every value is
transcribed from a cited publication (text statement or published figure).
Series here are **approximations for replication and visualization** — use
the cited papers' own data for publishable point estimates.

## confederate_amsterdam_monthly.csv

Monthly end-of-month prices (gold dollars, par = 100) of the Confederate 8%
gold bonds traded on the Amsterdam Stock Exchange, August 1863 – May 1865,
plus the December 1862/January 1863 pre-issue offer price.

- Source: Weidenmier, M. & Oosterlinck, K. (2007), *Victory or Repudiation?
  The Probability of the Southern Confederacy Winning the Civil War*, NBER
  WP 13567. Original data: *Amsterdamsch Effectenblad*, daily quotations
  1863–65 (~500 observations, not published in machine-readable form).
- `anchor` column records whether each value comes from an explicit number
  in the paper's text ("text") or is read off the paper's Figure 1
  ("figure"). Figure-read values are accurate to roughly ±2 gold dollars.
- The bond: 8% coupon paid semi-annually in specie, 10–20 year maturity
  (the analysis, like the paper, assumes 10 years); first coupon (Jan 1864)
  missed, so wartime prices embed arrears treatment (see paper's
  scenarios 1–3, which differ by <2 percentage points of probability).

## danish_london_1862_1865.csv

Prices of Danish government bonds marked in London around the
Schleswig-Holstein crisis and the war of 1864, hand-read from page scans of
*The Economist*'s weekly "Bankers' Price Current — Prices of Foreign
Stocks" table (archive.org, Serials in Microfilm collection,
`sim_economist_*`). OCR of the table columns is unusable, so every value
was read visually from the page image of the issue named in
`source_issue`; `date` is the weekday column in which the bargain is
marked. Method files: `scripts/fetch_danish_pages.py` documents the
scan-retrieval pipeline (leaf located via hOCR word coordinates).

Three caveats transcribed onto the analysis:

1. **These are marked bargains, not continuous quotes.** The London market
   in Danish sovereigns was very thin: in most weeks of 1862-65 *no*
   Danish bargain is marked at all, including the entire invasion phase
   (Feb-Apr 1864) for the older bonds. Silence is informative about
   liquidity, not about price.
2. Issues covered: the 3% loan of 1825 (Wilson/Hambro), the 4% loan of
   1863 (Hambro, issued March 1863 at ~91-92), and the 5% war loan of
   January 1864 (Hambro, 1.2m pounds, issued at 93; traded as
   partly-paid scrip - quoted per pounds paid, excluded here - until
   fully paid in May 1864).
3. `flag` = "xd" where the printed quote is marked ex-dividend; no
   coupon adjustment has been applied.

## Union greenback series (data/processed/greenback_monthly.csv)

Not in this directory but partially manual: parsed by
`bondwar.data_loaders.parse_mitchell_monthly` from the archive.org OCR of
Mitchell, W.C. (1908), *Gold, Prices, and Wages under the Greenback
Standard*, Table 2 — monthly average specie value of $100 in greenbacks,
compiled by E.B. Elliott (US Treasury) from four daily NY gold-room
quotations. Two months whose OCR is unreadable (Aug 1862, Apr 1863) are
overridden in code with 10000/gold-price-average from the same table rows;
all other values pass the reciprocal cross-check between the table's
gold-price and greenback-value columns to <0.8.
