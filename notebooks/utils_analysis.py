# notebooks/utils_analysis.py
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from statsmodels.tsa.seasonal import STL

# ---------- column helpers (robust to variants) ----------
def _pick_col(df: pd.DataFrame, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    # try case-insensitive
    lower_map = {c.lower(): c for c in df.columns}
    for c in candidates:
        if c.lower() in lower_map:
            return lower_map[c.lower()]
    raise KeyError(f"None of the candidate columns are present: {candidates}")

def _colnames(df: pd.DataFrame):
    area_col  = _pick_col(df, ["priceArea", "pricearea", "area", "PriceArea"])
    group_col = _pick_col(df, ["productionGroup", "productiongroup", "group", "ProductionGroup"])
    time_col  = _pick_col(df, ["startTime", "time", "timestamp", "datetime", "StartTime"])
    qty_col   = _pick_col(df, ["quantitykWh", "quantityKwh", "quantitykwh", "quantity", "quantity_kwh", "QuantitykWh"])
    return area_col, group_col, time_col, qty_col

# ---------- series builder ----------
def _series(df: pd.DataFrame, area: str, group: str) -> pd.Series:
    area_col, group_col, time_col, qty_col = _colnames(df)

    # ensure datetime
    if not np.issubdtype(df[time_col].dtype, np.datetime64):
        df = df.copy()
        df[time_col] = pd.to_datetime(df[time_col], utc=True, errors="coerce")

    ts = (
        df[(df[area_col] == area) & (df[group_col] == group)]
        .sort_values(time_col)[[time_col, qty_col]]
        .set_index(time_col)[qty_col]
        .asfreq("H")
        .interpolate(limit_direction="both")
    )
    return ts

def _ensure_stl_params(ts_len: int, period: int, seasonal: int, trend: int):
    if period < 2:
        period = 2
    max_period = max(2, ts_len // 3)
    if period > max_period:
        period = max_period

    trend = int(trend)
    if trend <= period:
        trend = period + 1
    if trend % 2 == 0:
        trend += 1
    if trend < 3:
        trend = 3

    seasonal = int(seasonal)
    if seasonal < 7:
        seasonal = 7
    return period, seasonal, trend

# ---------- STL ----------
def stl_production_plot(
    df: pd.DataFrame,
    area: str,
    group: str,
    period: int = 24 * 7,
    seasonal: int = 13,
    trend: int = 31,
    robust: bool = True,
):
    ts = _series(df, area, group)
    if ts.empty:
        return go.Figure(), False, f"No rows for (area={area}, group={group})."

    period, seasonal, trend = _ensure_stl_params(len(ts.dropna()), period, seasonal, trend)

    res = STL(ts, period=period, seasonal=seasonal, trend=trend, robust=robust).fit()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ts.index, y=ts.values, name="Observed", mode="lines"))
    fig.add_trace(go.Scatter(x=ts.index, y=res.trend, name="Trend", mode="lines"))
    fig.add_trace(go.Scatter(x=ts.index, y=res.seasonal, name="Seasonal", mode="lines"))
    fig.add_trace(go.Scatter(x=ts.index, y=res.resid, name="Resid", mode="lines"))
    fig.update_layout(
        title=f"STL — {area}/{group} (period={period}, trend={trend}, seasonal={seasonal})",
        xaxis_title="time", yaxis_title="quantity kWh", legend=dict(orientation="h"),
        height=420
    )
    return fig, True, ""

# ---------- Spectrogram ----------
def spectrogram_production_plot(
    df: pd.DataFrame,
    area: str,
    group: str,
    window_len: int = 24 * 7,
    overlap: float = 0.5,
    polar: bool = False,
):
    x = _series(df, area, group)
    if x.empty:
        return go.Figure(), False, f"No rows for (area={area}, group={group})."

    x = x.values.astype(float)
    N = len(x)
    w = int(window_len)
    if w < 32:
        w = 32
    step = max(1, int(w * (1 - overlap)))
    if step < 1:
        step = 1
    if N < w:
        return go.Figure(), False, "Series too short for selected window."

    win = np.hanning(w)
    starts = np.arange(0, N - w + 1, step)
    if len(starts) < 2:
        return go.Figure(), False, "Too few windows; increase overlap or reduce window length."

    spec_list = []
    for s in starts:
        seg = x[s:s + w] * win
        fft = np.fft.rfft(seg)
        mag = np.abs(fft)
        spec_list.append(mag)

    S = np.stack(spec_list, axis=1)
    freqs = np.fft.rfftfreq(w, d=3600)     # 1h step
    cycles_per_day = freqs * 3600 * 24

    if polar:
        power = S.mean(axis=1)
        fig = go.Figure()
        fig.add_trace(go.Barpolar(theta=cycles_per_day, r=power, name="avg power"))
        fig.update_layout(
            title=f"Polar periodogram — {area}/{group} (avg over windows)",
            polar=dict(radialaxis=dict(showline=False)),
            height=420
        )
        return fig, True, ""
    else:
        fig = go.Figure(
            data=go.Heatmap(
                z=20 * np.log10(S + 1e-9),
                x=np.arange(S.shape[1]),
                y=cycles_per_day,
                coloraxis="coloraxis",
            )
        )
        fig.update_layout(
            title=f"Spectrogram — {area}/{group}  (window={w}h, overlap={overlap:.2f})",
            xaxis_title="window index",
            yaxis_title="cycles/day",
            coloraxis=dict(colorscale="Turbo"),
            height=420
        )
        return fig, True, ""

# ---------- availability map ----------
def combos_available(df: pd.DataFrame):
    area_col, group_col, time_col, qty_col = _colnames(df)
    c = (
        df.groupby([area_col, group_col])[qty_col]
        .size()
        .reset_index(name="n")
        .sort_values([area_col, group_col])
    )
    d = {}
    for r in c.itertuples(index=False):
        d.setdefault(getattr(r, area_col), []).append(getattr(r, group_col))
    return d, c.rename(columns={area_col: "priceArea", group_col: "productionGroup"})
