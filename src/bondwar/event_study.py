"""Event-study machinery: largest moves, structural breaks, event windows.

Follows Willard, Guinnane & Rosen (1996) and Frey & Waldenström (2004):
identify the observations where the market moved most, then ask what news
arrived; and, separately, test whether named battles/campaigns moved the
market more than ordinary wartime noise.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def log_returns(series: pd.Series) -> pd.Series:
    s = series.dropna().astype(float)
    return np.log(s).diff().dropna()


def largest_moves(series: pd.Series, k: int = 12, window: int = 1) -> pd.DataFrame:
    """The k largest absolute log-price moves over `window` periods.

    Returns end-of-move date, cumulative % change and direction.
    """
    r = log_returns(series)
    if window > 1:
        r = r.rolling(window).sum().dropna()
    top = r.abs().sort_values(ascending=False).head(k)
    out = pd.DataFrame({
        "date": top.index,
        "pct_change": (np.exp(r.loc[top.index]) - 1) * 100,
    }).set_index("date").sort_index()
    return out


def match_events(moves: pd.DataFrame, events: pd.DataFrame,
                 tolerance_days: int = 45) -> pd.DataFrame:
    """Attach the nearest chronology event to each large market move.

    `events` needs columns [date, event]; extra columns are carried along.
    Monthly quotes react to news with a lag (news travel + end-of-month
    stamping), so the nearest event *before or shortly after* the quote
    within `tolerance_days` is reported.
    """
    ev = events.sort_values("date").reset_index(drop=True)
    rows = []
    for dt, row in moves.iterrows():
        delta = (dt - ev["date"]).dt.days
        cand = ev[(delta >= -10) & (delta <= tolerance_days)]
        if len(cand):
            # a month-end quote reacts to news *during* the month: prefer the
            # nearest event at-or-before the quote date over later ones
            deltas = (dt - cand["date"]).dt.days
            before = cand[deltas >= 0]
            pick_from = before if len(before) else cand
            nearest = pick_from.iloc[
                (dt - pick_from["date"]).dt.days.abs().argmin()]
            rows.append({"date": dt, "pct_change": row["pct_change"],
                         "candidate_event": nearest["event"],
                         "event_date": nearest["date"],
                         "days_after_event": (dt - nearest["date"]).days})
        else:
            rows.append({"date": dt, "pct_change": row["pct_change"],
                         "candidate_event": None, "event_date": pd.NaT,
                         "days_after_event": np.nan})
    return pd.DataFrame(rows).set_index("date")


def structural_breaks(series: pd.Series, n_bkps: int = 6) -> list[pd.Timestamp]:
    """Endogenous break dates in the (log) price level via binary segmentation."""
    import ruptures as rpt

    s = series.dropna().astype(float)
    sig = np.log(s.values).reshape(-1, 1)
    algo = rpt.Binseg(model="l2").fit(sig)
    idx = algo.predict(n_bkps=n_bkps)[:-1]  # last element is len(sig)
    return [s.index[i] for i in idx]


def event_window_study(series: pd.Series, events: pd.DataFrame,
                       pre: int = 1, post: int = 2,
                       benchmark: pd.Series | None = None) -> pd.DataFrame:
    """Cumulative (abnormal) return around each chronology event.

    Works in *periods of the series' own frequency* (months for monthly
    data). The return from `pre` periods before the event to `post`
    periods after is compared with the series' full-sample volatility to
    give a z-score. If `benchmark` is given, its matching return is
    subtracted first (abnormal return).
    """
    r = log_returns(series)
    if benchmark is not None:
        rb = log_returns(benchmark).reindex(r.index).fillna(0.0)
        r = r - rb
    sigma = r.std()
    rows = []
    for _, ev in events.iterrows():
        # first observation at/after the event date
        after = r.index[r.index >= ev["date"] - pd.Timedelta(days=15)]
        if not len(after):
            continue
        i = r.index.get_loc(after[0])
        lo, hi = max(0, i - pre + 1), min(len(r), i + post + 1)
        window = r.iloc[lo:hi]
        if not len(window):
            continue
        car = window.sum()
        rows.append({
            "event": ev["event"], "event_date": ev["date"],
            "window": f"{window.index[0].date()}..{window.index[-1].date()}",
            "car_pct": (np.exp(car) - 1) * 100,
            "z": car / (sigma * np.sqrt(len(window))) if sigma > 0 else np.nan,
        })
    out = pd.DataFrame(rows)
    if len(out):
        out = out.sort_values("car_pct", key=lambda s: s.abs(), ascending=False)
    return out
