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
    stamping), so the nearest event *at or before* the quote date within
    `tolerance_days` is reported. Events after the quote date are never
    matched: a price stamped at month-end cannot react to later news, and
    allowing it would smuggle look-ahead into the attribution.
    """
    ev = events.sort_values("date").reset_index(drop=True)
    rows = []
    for dt, row in moves.iterrows():
        delta = (dt - ev["date"]).dt.days
        cand = ev[(delta >= 0) & (delta <= tolerance_days)]
        if len(cand):
            nearest = cand.iloc[(dt - cand["date"]).dt.days.argmin()]
            rows.append({"date": dt, "pct_change": row["pct_change"],
                         "candidate_event": nearest["event"],
                         "event_date": nearest["date"],
                         "days_after_event": (dt - nearest["date"]).days})
        else:
            rows.append({"date": dt, "pct_change": row["pct_change"],
                         "candidate_event": None, "event_date": pd.NaT,
                         "days_after_event": np.nan})
    return pd.DataFrame(rows).set_index("date")


def chance_match_rate(series: pd.Series, events: pd.DataFrame,
                      tolerance_days: int = 45) -> float:
    """Placebo baseline for `match_events`: the share of *all* observation
    dates that would match some chronology event under the same rule.

    With a dense chronology and a generous tolerance nearly every date
    "matches" something, and the largest-moves table degenerates into
    storytelling. Report this alongside the table: attributions are only
    informative to the extent the matched moves beat this base rate in
    specificity (small `days_after_event`) and sign-consistency.
    """
    dates = series.dropna().index
    ev_dates = events["date"].dropna().sort_values()
    hits = sum(
        bool(((dt - ev_dates).dt.days.between(0, tolerance_days)).any())
        for dt in dates)
    return hits / len(dates) if len(dates) else np.nan


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
    periods after is compared with the series' *non-event* volatility to
    give a z-score: the null (sigma) is estimated from the observations
    outside every event window, as in a standard event-study estimation
    window - estimating sigma from the full sample would let the event
    shocks themselves inflate the null and bias every z toward zero.
    If `benchmark` is given, its matching return is subtracted first
    (abnormal return). Windows of nearby events can overlap; overlapping
    CARs share observations and are not independent tests, so the output
    flags them (`overlaps`).
    """
    r = log_returns(series)
    if benchmark is not None:
        rb = log_returns(benchmark).reindex(r.index).fillna(0.0)
        r = r - rb
    # locate each event's window first, so sigma can exclude all of them
    windows = []
    for _, ev in events.iterrows():
        # first observation at/after the event date (15-day grace: a
        # month-end quote already embeds an event from late that month)
        after = r.index[r.index >= ev["date"] - pd.Timedelta(days=15)]
        if not len(after):
            continue
        i = r.index.get_loc(after[0])
        lo, hi = max(0, i - pre + 1), min(len(r), i + post + 1)
        if hi > lo:
            windows.append((ev, lo, hi))
    in_any_window = np.zeros(len(r), dtype=bool)
    for _, lo, hi in windows:
        in_any_window[lo:hi] = True
    est = r[~in_any_window]
    sigma = est.std() if len(est) >= 12 else r.std()
    rows = []
    for ev, lo, hi in windows:
        window = r.iloc[lo:hi]
        car = window.sum()
        rows.append({
            "event": ev["event"], "event_date": ev["date"],
            "window": f"{window.index[0].date()}..{window.index[-1].date()}",
            "car_pct": (np.exp(car) - 1) * 100,
            "z": car / (sigma * np.sqrt(len(window))) if sigma > 0 else np.nan,
            "overlaps": False,  # filled below
            "_lo": lo, "_hi": hi,
        })
    out = pd.DataFrame(rows)
    if len(out):
        spans = out[["_lo", "_hi"]].to_numpy()
        out["overlaps"] = [
            bool(((spans[:, 0] < hi) & (spans[:, 1] > lo)).sum() > 1)
            for lo, hi in spans]
        out = (out.drop(columns=["_lo", "_hi"])
               .sort_values("car_pct", key=lambda s: s.abs(), ascending=False))
    return out
