# Bond-Event-Study

Using sovereign bond prices on neutral exchanges to estimate the market's
implied probability of each side winning a war, plus event studies of the
battles and political shocks that most moved those beliefs — for six wars:
the US Civil War, WW1, the Russian Civil War, WW2, Vietnam, and Iran–Iraq
(the last two are documented negative results: no traded instrument exists).

- **[RESEARCH_PLAN.md](RESEARCH_PLAN.md)** — theory, data strategy, methodology
- **[REPORT.md](REPORT.md)** — findings per war and cross-war conclusions
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
```

The processed CSVs are committed, so the analysis scripts run without the
90 MB raw download.

## Layout

```
src/bondwar/          two-state pricing model, event-study tools, loaders
data/raw/             downloaded sources (+ SOURCES.md); big files gitignored
data/manual/          literature-anchored series (+ PROVENANCE.md)
data/processed/       tidy monthly series used by the analyses
data/events/          battle/political chronologies per war
analysis/             one runnable script per war
output/               figures (png) and tables (csv)
```

## Data sources

NBER Macrohistory (consol/rente yields); Yale ICF Investor's Monthly Manual
(London sovereign prices 1869–1929); Frey & Waldenström's Zurich/Stockholm
WW2 bond prices (author-posted); Mitchell (1908) greenback gold values
(public-domain scan, OCR-parsed); Weidenmier & Oosterlinck (2007) Confederate
Amsterdam anchors. Full citations in `data/raw/SOURCES.md` and
`data/manual/PROVENANCE.md`.
