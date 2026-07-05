"""Loaders/parsers that turn raw downloaded sources into tidy monthly series.

Raw inputs live in data/raw (see data/raw/SOURCES.md for URLs); the
functions here are called by scripts/prepare_data.py, which writes the
cleaned CSVs in data/processed that the analysis scripts consume.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


# ---------------------------------------------------------------- NBER ----
def load_nber_dat(path: Path, name: str) -> pd.Series:
    """NBER macrohistory .dat: 'YYYY  MM  value' rows, '.' = missing."""
    rows = []
    for line in Path(path).read_text().splitlines():
        parts = line.split()
        if len(parts) < 3 or not parts[0].isdigit():
            continue
        year, month, val = int(parts[0]), int(parts[1]), parts[2]
        if val in {".", ""}:
            continue
        rows.append((pd.Timestamp(year, month, 1) + pd.offsets.MonthEnd(0),
                     float(val)))
    s = pd.Series(dict(rows), name=name).sort_index()
    s.index.name = "date"
    return s


# ----------------------------------------------------------------- IMM ----
IMM_TARGETS = {
    # (country regex, compsecdes regex) -> output issuer/series name.
    # Both patterns are anchored matches; the same issue often changes its
    # printed description over the decades, so alternations splice the
    # variants into one series.
    ("RUSSIAN", r"^5 % 1906"): ("Russia", "5% State Loan 1906"),
    ("RUSSIAN", r"^4 1/2 % 1909"): ("Russia", "4.5% Loan 1909"),
    ("FRENCH", r"^(3 per cents\.|3 per cent\.,? Rentes|3 %,? Rentes)"):
        ("France", "3% Rentes"),
    ("FRENCH", r"^6 % (Sterling, 1870|New Redemable Sterling)"):
        ("France", "6% Morgan Loan 1870"),
    ("FRENCH", r"^5 % National, (18)?71$"):
        ("France", "5% National Loan 1871"),
    ("NORTH GERMAN( CONFEDERATION)?", r"^5 (%|per cent)"):
        ("North German Confederation", "5% Loan 1870"),
    ("GERMAN", r"^Imp(erial|\.) 3 %,?( (18)?91-(2-)?3)?$"):
        ("Germany", "Imperial 3% 1891-3"),
    ("AUSTRIAN", r"^4 % Gold Rentes"): ("Austria", "4% Gold Rentes"),
    ("ITALIAN", r"(3 1/2 %|5 %) .*"): ("Italy", "Rentes (London)"),
    ("JAPANESE", r"^4 % Ster.*1st"): ("Japan", "4% Sterling Loan"),
    ("DANISH", r"^4 (%|per cent\.),? 1850(-| and 18)61( do)?"):
        ("Denmark", "4% Loans 1850-61"),
    ("DANISH", r"^(5 % debentures, 1864|5 %, 1864|5 pr\. cnt\. Debenture)"):
        ("Denmark", "5% Loan 1864"),
    # --- Ottoman Empire (the 1865 General Debt is the workhorse series) ---
    # NB: ", 1874" excluded - that is the new 1874 loan, quoted as scrip
    # at a premium over paid-up value until Jan 1875
    ("TURKISH", r"^(5 p ct\. 1865|5 % General Debt(, '65|\.)?$"
                r"|5 % Genrl\. Debt|Registered General Debt)"):
        ("Turkey", "5% General Debt 1865"),
    ("TURKISH", r"^(6 per cent\. 1858|6 %, 1858|Registered, 1858)"):
        ("Turkey", "6% Loan 1858 (Customs)"),
    ("TURKISH", r"^4 (%, guaranteed by England and France, 1855"
                r"|per cent\. guaranteed by British & French Gov\."
                r"|%, '55 gtd\. by Eng\. & France|%, g\. by Englnd & France)"):
        ("Turkey", "4% 1855 (Anglo-French guarantee)"),
    ("TURKISH", r"^Converted - S(e)?ries A 1 %|^Converted - B 1 %"):
        ("Turkey", "Converted (Muharrem) Series A/B"),
    ("TURKISH", r"^4 % Unified"): ("Turkey", "4% Unified Debt"),
    ("TURKISH", r"^4 % 1891$"): ("Turkey", "4% Loan 1891"),
    ("TURKISH", r"^3 1/2 % 1894$"): ("Turkey", "3.5% Loan 1894"),
    # --- China: Qing and Republican foreign debt ---
    ("CHINESE", r"^8 %,? 1874-6$"): ("China", "8% Loan 1874-6"),
    ("CHINESE", r"^8 %, 1877$"): ("China", "8% Loan 1877"),
    ("CHINESE", r"^Series A, 7 %$"): ("China", "7% Loan Series A"),
    ("CHINESE", r"^7 % Silver Loan,? ('|18)?94"):
        ("China", "7% Silver Loan 1894"),
    ("CHINESE", r"^6 % (Gold|Gld)"): ("China", "6% Gold Loan 1895"),
    ("CHINESE", r"^5 %,? 1896$"): ("China", "5% Gold Loan 1896"),
    ("CHINESE", r"^4 1/2 % Gold Bonds, 1898"):
        ("China", "4.5% Gold Loan 1898"),
    ("CHINESE", r"^5 % Hukuang"): ("China", "5% Hukuang Railways 1911"),
    ("CHINESE", r"^5 % Reorg"): ("China", "5% Reorganisation Loan 1913"),
    ("CHINESE", r"^8 % (Treasury Bills|Stg\. Treas)"):
        ("China", "8% Sterling Treasury 1920s"),
}


def _num(x):
    try:
        v = float(x)
        return v if 0 < v < 300 else np.nan
    except (TypeError, ValueError):
        return np.nan


# The IMM quotes new loans as scrip at a *premium over the paid-up issue
# price* until they are fully paid; those readings (single digits) are not
# comparable with per-100 bond prices, so series known to begin life as
# scrip get a floor below which quotes are discarded.
PRICE_FLOORS = {
    "6% Morgan Loan 1870": 20.0,
    "5% National Loan 1871": 20.0,
    "5% Loan 1870": 20.0,
    # Jul 1913: partly-paid scrip in the 50s; fully-paid quotes ~90 from Aug
    "5% Reorganisation Loan 1913": 60.0,
}

# Known-bad readings, dropped after extraction. Jan-Mar 1871: the IMM shows
# no rente bargains in London (siege of Paris / Commune) and carries only a
# 'lastbusiness' placeholder of 80, inconsistent with every surrounding
# quote (54 in Dec 1870, 51 in Apr 1871) and with Paris levels; treat the
# months as missing rather than inventing a 50% rally.
BAD_QUOTES = {
    ("France", "3% Rentes"): ["1871-01", "1871-02", "1871-03"],
    # 132.5 sandwiched between months of ~107: a digit error in the source
    ("China", "6% Gold Loan 1895"): ["1899-02"],
}


def extract_imm_sovereigns(csv_path: Path) -> pd.DataFrame:
    """Pull monthly London prices for the target sovereign bonds from the
    Yale ICF Investor's Monthly Manual master file (Stocks_new.csv).

    Price preference: last-quoted price of the month, then last business
    day price, then the mid of the month's high/low. Returns a tidy frame
    [date, issuer, series, price].
    """
    usecols = ["year", "month", "country", "compsecdes",
               "pricemonthlate", "pricemonthlastday", "lastbusiness",
               "pricemonthopen", "pricemonthhigh", "pricemonthlow"]
    df = pd.read_csv(csv_path, usecols=usecols, low_memory=False)
    df["country"] = (df["country"].astype(str).str.upper()
                     .str.strip().str.rstrip("."))
    df["compsecdes"] = df["compsecdes"].astype(str).str.strip()

    frames = []
    for (country, pattern), (issuer, series) in IMM_TARGETS.items():
        sub = df[df["country"].str.fullmatch(country, na=False)
                 & df["compsecdes"].str.match(pattern)].copy()
        if not len(sub):
            continue
        for col in ["pricemonthlate", "pricemonthlastday", "lastbusiness",
                    "pricemonthopen", "pricemonthhigh", "pricemonthlow"]:
            sub[col] = sub[col].map(_num)
        # a 'latest price' far outside the month's own high-low range is a
        # transcription error (e.g. Turkish GD Oct 1872: late 72.75 vs
        # high 53.25); drop it so the fallback chain supplies the price
        hi, lo = sub["pricemonthhigh"], sub["pricemonthlow"]
        bad_late = (hi.notna() & lo.notna()
                    & ((sub["pricemonthlate"] > hi * 1.1)
                       | (sub["pricemonthlate"] < lo * 0.9)))
        sub.loc[bad_late, "pricemonthlate"] = np.nan
        mid = (sub["pricemonthhigh"] + sub["pricemonthlow"]) / 2
        sub["price"] = (sub["pricemonthlate"]
                        .fillna(sub["pricemonthlastday"])
                        .fillna(sub["lastbusiness"])
                        .fillna(mid)
                        .fillna(sub["pricemonthopen"]))
        floor = PRICE_FLOORS.get(series)
        if floor is not None:
            sub.loc[sub["price"] < floor, "price"] = np.nan
        sub = sub.dropna(subset=["price"])
        sub["date"] = pd.to_datetime(dict(year=sub.year, month=sub.month,
                                          day=1)) + pd.offsets.MonthEnd(0)
        g = (sub.groupby("date", as_index=False)["price"].median()
             .assign(issuer=issuer, series=series))
        bad = BAD_QUOTES.get((issuer, series))
        if bad:
            g = g[~g["date"].dt.strftime("%Y-%m").isin(bad)]
        frames.append(g)
    out = pd.concat(frames, ignore_index=True)
    return out[["date", "issuer", "series", "price"]].sort_values(
        ["issuer", "date"])


# ------------------------------------------------- Frey & Waldenström ----
def load_frey_waldenstrom() -> pd.DataFrame:
    """Monthly bond price indices, Zurich & Stockholm, 1933-48.

    Sources: Frey & Waldenström FHR 2004 (Germany/Belgium in both markets)
    and HSR 2008 (Germany/France in Zurich). Tidy frame
    [date, market, issuer, price].
    """
    frames = []

    def parse(fname, sheet, col_market_row=3, col_country_row=5):
        df = pd.read_excel(RAW / fname, sheet_name=sheet, header=None)
        markets = df.iloc[col_market_row, 1:].tolist()
        countries = df.iloc[col_country_row, 1:].tolist()
        data = df.iloc[6:, :].copy()
        dates = pd.to_datetime(data.iloc[:, 0], errors="coerce")
        for j, (mkt, ctry) in enumerate(zip(markets, countries), start=1):
            if not isinstance(ctry, str):
                continue
            vals = pd.to_numeric(data.iloc[:, j], errors="coerce")
            sub = pd.DataFrame({"date": dates, "price": vals.values})
            sub = sub.dropna()
            sub["market"] = str(mkt).strip()
            sub["issuer"] = str(ctry).strip()
            frames.append(sub)

    parse("frey_waldenstrom_fhr2004.xls", "Data")
    parse("frey_waldenstrom_hsr2008.xls", "Zurich data")
    out = pd.concat(frames, ignore_index=True)
    out = (out.groupby(["date", "market", "issuer"], as_index=False)["price"]
           .mean())
    return out[["date", "market", "issuer", "price"]].sort_values(
        ["market", "issuer", "date"])


# ------------------------------------------------------- Mitchell OCR ----
def parse_mitchell_monthly(txt_path: Path,
                           years=range(1862, 1866)) -> pd.DataFrame:
    """Monthly specie value of $100 in greenbacks from the OCR of
    Mitchell (1908), Table 2 (identical to Mitchell 1903, App. A, Table 1;
    original source: E.B. Elliott's US Treasury compilation of daily NY
    gold-room quotations).

    Table layout in the OCR: a year heading, then per month a name line
    followed by six numbers (gold price low/avg/high, greenback value
    high/avg/low). OCR digit errors are repaired by exploiting the
    reciprocal identity greenback_avg = 10000 / gold_avg.
    """
    text = Path(txt_path).read_text()
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    # Walk the Table 2 region: "1862."-style year headings, then per month a
    # name line followed by six cells. The two *average* columns are printed
    # with exactly one decimal place; the lowest/highest cells carry OCR-
    # garbled vulgar fractions. So within a month block the one-decimal
    # tokens are, in order, [gold price avg, greenback value avg].
    rows = []
    year = None
    month = None
    cells: list[float] = []

    def close_block():
        if year in years and month is not None and cells:
            gold_avg = cells[0] if len(cells) > 0 else np.nan
            gb_avg = cells[1] if len(cells) > 1 else np.nan
            rows.append((year, MONTHS.index(month) + 1, gold_avg, gb_avg))

    for ln in lines:
        ym = re.match(r"^(18\d\d)\.\s*$", ln)
        if ym:
            close_block()
            month, cells = None, []
            year = int(ym.group(1))
            continue
        if "quarter" in ln.lower() or ln.startswith("Year"):
            close_block()
            month, cells = None, []
            continue
        name = next((m for m in MONTHS if ln.startswith(m[:5])), None)
        if name:
            close_block()
            month, cells = name, []
            continue
        if month is not None and re.match(r"^\d{2,3}[.,]\d\s*$", ln):
            cells.append(float(ln.replace(",", ".")))
    close_block()

    df = pd.DataFrame(rows, columns=["year", "month", "gold_avg", "gb_avg"])
    df = df.drop_duplicates(["year", "month"]).sort_values(["year", "month"])

    # Reconcile with the reciprocal identity gb = 10000/gold, repairing
    # single-digit OCR confusions (8<->3, 5<->8 in the leading digit) in
    # whichever cell is corrupt.
    def reconcile(r):
        g0, b0 = r["gold_avg"], r["gb_avg"]
        digit_fixes = (0, -50, +50, -30, +30)
        best, best_err = np.nan, np.inf
        for dg in digit_fixes:
            for db in digit_fixes:
                g, b = g0 + dg, b0 + db
                if not (np.isfinite(g) and np.isfinite(b)):
                    continue
                if not (95 <= g <= 300 and 30 <= b <= 101):
                    continue
                err = abs(10000 / g - b)
                # prefer the untouched reading on ties
                err += 0.01 * ((dg != 0) + (db != 0))
                if err < best_err:
                    best_err, best = err, b
        if best_err < 0.8:
            return best
        # otherwise trust the gold-price average (the cleaner column)
        if np.isfinite(g0) and 95 <= g0 <= 300:
            return round(10000 / g0, 1)
        if np.isfinite(b0) and 30 <= b0 <= 101:
            return b0
        return np.nan

    df["greenback_gold_value"] = df.apply(reconcile, axis=1)

    # Months whose OCR is too garbled to parse ("AuiTUst" 1862; April 1863's
    # average carries a stray leading dot). Values are 10000/gold_avg using
    # the gold-price averages printed in the same table rows.
    overrides = {(1862, 8): 87.3, (1863, 4): 66.0}
    for (yy, mm), val in overrides.items():
        mask = (df["year"] == yy) & (df["month"] == mm)
        if mask.any():
            df.loc[mask & df["greenback_gold_value"].isna(),
                   "greenback_gold_value"] = val
        else:
            df = pd.concat([df, pd.DataFrame(
                [{"year": yy, "month": mm, "gold_avg": np.nan,
                  "gb_avg": np.nan, "greenback_gold_value": val}])],
                ignore_index=True)
    df = df.sort_values(["year", "month"])
    df["date"] = pd.to_datetime(dict(year=df.year, month=df.month,
                                     day=1)) + pd.offsets.MonthEnd(0)
    out = df[["date", "greenback_gold_value"]].dropna().set_index("date")
    # sanity: value of $100 currency in gold must lie in (30, 101)
    out = out[(out["greenback_gold_value"] > 30)
              & (out["greenback_gold_value"] <= 101)]
    return out
