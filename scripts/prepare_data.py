"""Build data/processed CSVs from the raw sources in data/raw.

Run scripts/fetch_data.sh first (downloads the raw files); then:

    python scripts/prepare_data.py

Outputs (all monthly unless noted):
    processed/nber_yields.csv          UK consols 1852-1938 (m13041b+c
                                       spliced), German yields 1870-1913, US
    processed/imm_sovereign_prices.csv London prices 1869-1929: Russia,
                                       France, Germany, Austria, Italy,
                                       Japan, Turkey, China, Denmark, the
                                       North German Confederation
    processed/ww2_bond_prices.csv      Zurich/Stockholm indices 1933-48
    processed/greenback_monthly.csv    Specie value of $100 greenbacks 1862-65
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bondwar import data_loaders as dl  # noqa: E402

RAW, PROCESSED = dl.RAW, dl.PROCESSED
PROCESSED.mkdir(parents=True, exist_ok=True)


def main():
    # ---- NBER macrohistory yields (percent p.a.) ----
    # NB: per the NBER chapter-13 catalog, m13028a is *Germany* bond yields
    # 1870-1913 (an earlier revision here mislabeled it as France) and
    # m13028b (Berlin 1924-31) is entirely missing values, so it is dropped.
    series = {
        "uk_consols": "nber_m13041c.dat",       # England, consols 1888-1938
        "uk_consols_3pct": "nber_m13041b.dat",  # England, 3% consols 1852-88
        "germany_yields": "nber_m13028a.dat",   # Germany, bond yields 1870-1913
        "us_longterm": "nber_m13033a.dat",      # US long-term bonds 1919-44
    }
    frames = []
    for name, fname in series.items():
        p = RAW / fname
        if p.exists():
            frames.append(dl.load_nber_dat(p, name))
        else:
            print(f"  ! missing {fname}, skipping")
    nber = pd.concat(frames, axis=1, sort=True)
    # splice the 3% consol yield (1852-88) onto the front of the consol
    # series so one column covers 1852-1938
    if "uk_consols_3pct" in nber:
        early = nber["uk_consols_3pct"]
        nber["uk_consols"] = nber["uk_consols"].fillna(early)
        nber = nber.drop(columns=["uk_consols_3pct"])
    nber.to_csv(PROCESSED / "nber_yields.csv")
    print(f"nber_yields.csv: {nber.shape}")

    # ---- Investor's Monthly Manual sovereign prices ----
    imm_file = RAW / "Stocks_new.csv"
    out_imm = PROCESSED / "imm_sovereign_prices.csv"
    if imm_file.exists():
        imm = dl.extract_imm_sovereigns(imm_file)
        imm.to_csv(out_imm, index=False)
        print(f"imm_sovereign_prices.csv: {imm.shape}, "
              f"issuers={sorted(imm.issuer.unique())}")
    elif out_imm.exists():
        print("IMM raw file absent; keeping existing processed extract")
    else:
        print("  ! IMM raw file absent and no processed extract present")

    # ---- Frey & Waldenström WW2 prices ----
    ww2 = dl.load_frey_waldenstrom()
    ww2.to_csv(PROCESSED / "ww2_bond_prices.csv", index=False)
    print(f"ww2_bond_prices.csv: {ww2.shape}, "
          f"series={ww2.groupby(['market','issuer']).size().to_dict()}")

    # ---- Greenback specie value (Mitchell OCR) ----
    ocr = RAW / "mitchell1908_table2_excerpt.txt"
    out_gb = PROCESSED / "greenback_monthly.csv"
    if ocr.exists():
        gb = dl.parse_mitchell_monthly(ocr)
        gb.to_csv(out_gb)
        print(f"greenback_monthly.csv: {gb.shape}, "
              f"range {gb.index.min().date()}..{gb.index.max().date()}")
    elif out_gb.exists():
        print("Mitchell OCR absent; keeping existing processed extract")
    else:
        print("  ! Mitchell OCR absent and no processed extract present")


if __name__ == "__main__":
    main()
