# Raw data sources

Downloaded by `scripts/fetch_data.sh`. Large files are gitignored; the
processed extracts in `data/processed/` are committed so the analyses run
without re-downloading.

| File | Source | Terms |
|---|---|---|
| `nber_m13041c.dat` | NBER Macrohistory ch.13, England: yield of consols, monthly 1888–1938 — https://data.nber.org/databases/macrohistory/rectdata/13/ | public |
| `nber_m13028a.dat` | NBER, France: security yields 1898–1939 | public |
| `nber_m13028b.dat` | NBER, Germany: bond yields 1870–1913 | public |
| `nber_m13033a.dat` | NBER, US: long-term bond yields 1919–44 | public |
| `frey_waldenstrom_fhr2004.xls` | Frey & Waldenström, *Markets Work in War* (Financial History Review 2004) — monthly German/Belgian bond prices, Zurich & Stockholm 1933–48. Author-posted: https://sites.google.com/view/danielwaldenstrom/data-programs | cite the paper |
| `frey_waldenstrom_hsr2008.xls` | Frey & Waldenström, *Using Financial Markets to Analyze History* (HSR 2008) — adds French bonds in Zurich; weekly Nordic yields 1938–40 | cite the paper |
| `Stocks_new.csv` (gitignored, 92 MB) | Yale ICF, *Investor's Monthly Manual* database (London Stock Exchange, monthly, 1869–1929) — https://som.yale.edu/.../london-stock-exchange | academic research use; cite Yale ICF |
| `mitchell1908_table2_excerpt.txt` | OCR (archive.org, Google scan) of W.C. Mitchell, *Gold, Prices, and Wages under the Greenback Standard* (1908), Table 2 | public domain |

Literature-derived (hand-entered) series live in `data/manual/` with their
own `PROVENANCE.md`.
