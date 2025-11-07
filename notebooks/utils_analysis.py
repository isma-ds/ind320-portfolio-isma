import numpy as np
import pandas as pd
import plotly.express as px
from statsmodels.tsa.seasonal import STL

# ---------- Column normalizer ----------
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "StartTime": "startTime",
        "start_time": "startTime",
        "Quantity": "quantitykWh",
        "quantity": "quantitykWh",
        "quantity_kwh": "quantitykWh",
        "QuantityKWh": "quantitykWh",
    }
    return df.rename(columns={c: rename_map.get(c, c) for c in df.columns})

# ---------- Safe series selector ----------
def _series(df: pd.DataFrame, area: str, group: str) -> pd.DataFrame:
    df = normalize_columns(df)
    need = {"priceArea", "productionGroup", "startTime", "quantitykWh"}
    if not need.issubset(df.columns):
        missing = need - set(df.columns)
        raise KeyError(f"Missing columns in dataframe: {missing}")

    ts = (
        df[(df["priceArea"] == area) & (df["productionGroup"] == group)]
        .sort_values("startTime")[["startTime", "quantitykWh"]]
        .dropna()
        .reset_index(drop=True)
    )
    if ts.empty:
        raise ValueError(f"No data for area={area}, group={group}")
    ts["startTime"] = pd.to_datetime(ts["startTime"], utc=True, errors="coerce")
    ts = ts.dropna(subset=["startTime"])
    return ts

# ---------- STL ----------
def stl_production_plot(
    df: pd.DataFrame,
    area: str = "NO5",
    group: str = "Hydro",
    period: int = 24 * 7,
    seasonal: int = 13,
    trend: int = 31,
    robust: bool = True,
):
    ts = _series(df, area, group).set_index("startTime")["quantitykWh"]

    res = STL(ts, period=period, seasonal=seasonal, trend=trend, robust=robust).fit()
    decomp = pd.DataFrame(
        {
            "time": ts.index,
            "Observed": res.observed,
            "Trend": res.trend,
            "Seasonal": res.seasonal,
            "Residual": res.resid,
        }
    )
    fig = px.line(
        decomp.melt(id_vars="time", var_name="Component", value_name="kWh"),
        x="time",
        y="kWh",
        color="Component",
        title=f"STL Decomposition — {area} / {group}",
    )
    fig.update_layout(
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        font=dict(color="white"),
        hovermode="x unified",
        margin=dict(l=40, r=20, t=60, b=40),
        legend_title="Component",
    )
    return fig

# ---------- Spectrogram (NumPy-based) ----------
def spectrogram_production_plot(
    df: pd.DataFrame,
    area: str = "NO5",
    group: str = "Hydro",
    window_len: int = 24 * 7,
    overlap: float = 0.5,
    title: str = "Spectrogram — Production",
):
    ts = _series(df, area, group)
    y = ts["quantitykWh"].to_numpy(dtype=float)
    n = len(y)
    win = int(window_len)
    step = max(1, int(win * (1 - overlap)))
    if win < 8 or step < 1 or win > n:
        raise ValueError("Bad window/overlap relative to series length")

    # simple Hann window + FFT magnitude
    hann = 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(win) / (win - 1))
    slices = []
    for start in range(0, n - win + 1, step):
        seg = (y[start : start + win] - np.mean(y[start : start + win])) * hann
        spec = np.abs(np.fft.rfft(seg))  # magnitude
        slices.append(spec)
    S = np.array(slices)  # frames x freq

    # Axes: x = frame time, y = frequency index (cycles per window)
    times = ts["startTime"].iloc[0 : 0 + len(slices) * step : step]
    if len(times) != S.shape[0]:
        times = pd.date_range(ts["startTime"].iloc[0], periods=S.shape[0], freq=f"{step}H")

    freq_idx = np.arange(S.shape[1])  # arbitrary frequency bins

    Z = pd.DataFrame(S, columns=freq_idx)
    Z["time"] = times
    Z = Z.melt(id_vars="time", var_name="freq_bin", value_name="power")

    fig = px.density_heatmap(
        Z,
        x="time",
        y="freq_bin",
        z="power",
        nbinsx=min(100, S.shape[0]),
        nbinsy=min(60, S.shape[1]),
        title=f"{title} — {area}/{group}",
    )
    fig.update_layout(
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        font=dict(color="white"),
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig
