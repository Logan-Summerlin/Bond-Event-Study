"""Shared setup for the per-war analysis scripts."""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

PROCESSED = ROOT / "data" / "processed"
MANUAL = ROOT / "data" / "manual"
EVENTS = ROOT / "data" / "events"
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)


def load_events(name: str) -> pd.DataFrame:
    ev = pd.read_csv(EVENTS / f"{name}.csv", parse_dates=["date"])
    return ev.sort_values("date").reset_index(drop=True)


def load_imm() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED / "imm_sovereign_prices.csv",
                     parse_dates=["date"])
    return df


def imm_series(issuer: str, series: str | None = None,
               start=None, end=None) -> pd.Series:
    df = load_imm()
    df = df[df.issuer == issuer]
    if series is not None:
        df = df[df.series == series]
    s = df.set_index("date")["price"].sort_index()
    return s.loc[start:end]


def load_nber() -> pd.DataFrame:
    return pd.read_csv(PROCESSED / "nber_yields.csv", parse_dates=["date"]
                       ).set_index("date")


def save_table(df: pd.DataFrame, name: str, float_fmt="%.2f"):
    path = OUT / f"{name}.csv"
    df.to_csv(path, float_format=float_fmt)
    print(f"  wrote {path.relative_to(ROOT)}")


def save_fig(fig, name: str, footnote: str | None = None):
    from bondwar import plotting

    path = OUT / f"{name}.png"
    plotting.save_fig(fig, path, footnote=footnote)
    print(f"  wrote {path.relative_to(ROOT)}")
