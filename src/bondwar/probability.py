"""Two-state pricing model: extracting market-implied victory probabilities.

The core identity (risk-neutral, following Weidenmier & Oosterlinck 2007,
Frey & Kucher 2000):

    P_t = pi_t * V_win + (1 - pi_t) * V_lose
    pi_t = (P_t - V_lose) / (V_win - V_lose)

where
    P_t     observed market price of the belligerent's bond,
    V_win   value of the bond conditional on the issuer's victory
            (promised cash flows discounted at a neutral risk-free yield),
    V_lose  value conditional on defeat (recovery).

`pi_t` is the probability of *debt survival*, which we interpret as the
probability of victory under the stated recovery assumptions.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def bond_pv(coupon_rate: float, maturity_years: float, rf_yield: float,
            face: float = 100.0, freq: int = 2) -> float:
    """Present value per `face` of a coupon bond discounted at `rf_yield`.

    This is V_win: what the bond would be worth if default risk vanished.
    Rates are decimals (0.05 = 5%).
    """
    n = int(round(maturity_years * freq))
    c = coupon_rate * face / freq
    y = rf_yield / freq
    if y <= 0:
        return c * n + face
    ann = c * (1 - (1 + y) ** -n) / y
    return ann + face * (1 + y) ** -n


def perpetuity_pv(coupon_rate: float, rf_yield: float, face: float = 100.0) -> float:
    """V_win for a perpetual bond (rente/consol-style): coupon / rf yield."""
    return coupon_rate * face / rf_yield


def implied_prob(price, v_win, v_lose=0.0, clip: bool = True):
    """pi = (P - V_lose) / (V_win - V_lose). Works on scalars or Series."""
    pi = (price - v_lose) / (v_win - v_lose)
    if clip:
        pi = np.clip(pi, 0.0, 1.0)
    return pi


def implied_prob_series(prices: pd.Series,
                        rf_yields: pd.Series | float,
                        coupon_rate: float,
                        maturity_years: float | None,
                        recovery_frac: float = 0.0,
                        face: float = 100.0,
                        freq: int = 2) -> pd.Series:
    """Victory-probability path for a bond price series.

    V_win is recomputed each period from the contemporaneous risk-free
    yield so that world-interest-rate moves do not masquerade as war news.
    `recovery_frac` expresses V_lose as a fraction of V_win.
    `maturity_years=None` treats the bond as a perpetuity.
    """
    idx = prices.index
    if np.isscalar(rf_yields):
        rf = pd.Series(float(rf_yields), index=idx)
    else:
        rf = rf_yields.reindex(idx).ffill()
    v_win = rf.apply(
        lambda y: perpetuity_pv(coupon_rate, y, face) if maturity_years is None
        else bond_pv(coupon_rate, maturity_years, y, face, freq)
    )
    # A survivor's bond wouldn't trade above its risk-free PV; cap so that
    # pre-war "normal" prices map to pi ~= 1 rather than pi > 1.
    v_lose = recovery_frac * v_win
    return implied_prob(prices, v_win, v_lose)


def currency_implied_prob(gold_value: pd.Series,
                          v_resume: float = 100.0,
                          v_collapse: float = 0.0) -> pd.Series:
    """Two-state model applied to an inconvertible wartime currency.

    `gold_value` is the specie value of 100 units of paper currency (e.g.
    the gold price of $100 in greenbacks). `v_resume` is its value if the
    issuer wins and resumes convertibility (<=100 because resumption comes
    only after some delay); `v_collapse` its value if the issuer loses.
    """
    return implied_prob(gold_value, v_resume, v_collapse)


def prob_bands(prices: pd.Series, rf_yields, coupon_rate, maturity_years,
               recoveries=(0.0, 0.25, 0.5), **kw) -> pd.DataFrame:
    """Probability paths under several recovery assumptions -> DataFrame."""
    out = {}
    for r in recoveries:
        out[f"recovery_{int(r * 100)}pct"] = implied_prob_series(
            prices, rf_yields, coupon_rate, maturity_years, r, **kw)
    return pd.DataFrame(out)
