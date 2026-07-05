# Bond-Event-Study

Using sovereign bond prices on neutral exchanges to estimate the market's
implied probability of each side winning a war (or a state surviving its
fiscal crisis), plus event studies of the battles and political shocks that
most moved those beliefs — for ten conflicts:

- **US Civil War, WW1, Russian Civil War, WW2** — full probability-path
  treatment;
- **Vietnam, Iran–Iraq** — documented negative results (no traded
  instrument exists);
- **Denmark & the Schleswig-Holstein war of 1864** — hand-collected London
  bargains read from page scans of *The Economist* (pre-dating the IMM);
- **Franco-Prussian War 1870–71** — French rentes vs the North German
  Confederation's London war loan;
- **China 1885–1929** — Qing and Republican sterling debt (Sino-Japanese
  war, Boxer summer, the 1911 revolution, the warlord decade);
- **The Ottoman decline 1869–1929** — sixty years from the 1875 default
  through Lausanne, across collateral tiers.

- **[RESEARCH_PLAN.md](RESEARCH_PLAN.md)** — theory, data strategy, methodology
- **[REPORT.md](REPORT.md)** — findings per conflict and cross-war conclusions
- `output/` — figures and turning-point tables (committed)

## Reproduce

```bash
pip install -r requirements.txt
bash scripts/fetch_data.sh        # downloads raw sources (~110 MB, mostly Yale IMM)
python scripts/prepare_data.py    # builds data/processed/*.csv
python analysis/01_us_civil_war.py
python analysis/02_ww1.py
python analysis/03_russian_civil_war.py
python analysis/04_ww2.py
python analysis/05_vietnam_war.py
python analysis/06_iran_iraq.py
python analysis/07_schleswig_1864.py
python analysis/08_franco_prussian.py
python analysis/09_china.py
python analysis/10_ottoman.py
```

The processed CSVs are committed, so the analysis scripts run without the
90 MB raw download. The Danish 1862–65 series is hand-read from archive.org
page scans (see `data/manual/PROVENANCE.md`); `scripts/fetch_danish_pages.py`
re-downloads the scan strips it was read from.

## Layout

```
src/bondwar/          two-state pricing model, event-study tools, loaders
data/raw/             downloaded sources (+ SOURCES.md); big files gitignored
data/manual/          literature/scan-anchored series (+ PROVENANCE.md)
data/processed/       tidy monthly series used by the analyses
data/events/          battle/political chronologies per conflict
analysis/             one runnable script per conflict
output/               figures (png) and tables (csv)
```

## Data sources

NBER Macrohistory (consol yields 1852–1938, German yields 1870–1913); Yale
ICF Investor's Monthly Manual (London sovereign prices 1869–1929: Russia,
France, Germany, Austria, Italy, Japan, Turkey, China, Denmark, the North
German Confederation); Frey & Waldenström's Zurich/Stockholm WW2 bond
prices (author-posted); Mitchell (1908) greenback gold values
(public-domain scan, OCR-parsed); Weidenmier & Oosterlinck (2007)
Confederate Amsterdam anchors; The Economist's Bankers' Price Current
1862–65 (archive.org scans, hand-read Danish quotes). Full citations in
`data/raw/SOURCES.md` and `data/manual/PROVENANCE.md`.
