# notebooks/utils_analysis.py
import numpy as np
import pandas as pd
import plotly.express as px
from pathlib import Path
from statsmodels.tsa.seasonal import STL
import plotly.graph_objects as go

# ---------- Robust production CSV loader ----------
def load_production_csv(path: str | Path = "data/production_per_group_mba_hour.csv") -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Production CSV not found at {p.resolve()}")

    df = pd.read_csv(p)

    # Normalize header names (trim & unify case)
    df.columns = df.columns.str.strip()

    # Common header variants → standard names
    rename_map = {}
    for c in df.columns:
        lc = c.lower()
        if lc == "pricearea":        rename_map[c] = "priceArea"
        elif lc == "productiongroup":rename_map[c] = "productionGroup"
        elif lc in ("starttime", "start_time"): rename_map[c] = "startTime"
        elif lc in ("quantitykwh", "quantity_kwh", "quantity", "kwh"): rename_map[c] = "quantityKwh"
    if rename_map:
        df = df.rename(columns=rename_map)

    required = {"priceArea", "productionGroup", "startTime", "quantityKwh"}
    missing = required.difference(df.columns)
    if missing:
        raise KeyError(f"Production CSV missing columns: {sorted(missing)} — columns present: {list(df.columns)}")

    # Parse time, force UTC and hour frequency later
    df["startTime"] = pd.to_datetime(df["startTime"], utc=True, errors="coerce")
    df = df.dropna(subset=["startTime"])
    # Ensure numeric
    df["quantityKwh"] = pd.to_numeric(df["quantityKwh"], errors="coerce").fillna(0)

    return df


# ---------- Internal series builder (safe) ----------
def _series(df: pd.DataFrame, area: str, group: str) -> pd.Series:
    if df.empty:
        raise ValueError("Production dataframe is empty.")

    # Filter
    part = df[(df["priceArea"] == area) & (df["productionGroup"] == group)].copy()
    if part.empty:
        # Help message that shows what combinations exist
        have = (
            df.groupby(["priceArea", "productionGroup"])["quantityKwh"]
            .size().reset_index().rename(columns={"quantityKwh":"n"})
        )
        raise ValueError(
            f"No rows for (area={area}, group={group}). "
            f"Available combos:\n{have.head(20).to_string(index=False)}"
        )

    # Sort, select and hourly index
    part = part.sort_values("startTime")[["startTime", "quantityKwh"]]
    ts = (
        part.set_index("startTime")["quantityKwh"]
        .asfreq("H")
        .interpolate(limit_direction="both")
    )
    return ts


# ---------- STL (auto-safe) ----------
def stl_production_plot(
    df: pd.DataFrame,
    area: str = "NO5",
    group: str = "Hydro",
    period_hours: int = 24 * 7,
    seasonal: int = 13,
    trend: int = 31,
    robust: bool = True,
    title: str = "STL — Production"
):
    ts = _series(df, area, group)

    # If the series is short, adjust period/trend safely
    valid_len = int(ts.dropna().shape[0])
    if valid_len < 10:
        raise ValueError(f"Series too short for STL (len={valid_len}).")

    # Period must be >= 2 and <= len/2 to make sense
    period = max(2, min(period_hours, valid_len // 2))
    # Trend must be odd, ≥3 and > period
    trend_adj = int(trend)
    if trend_adj <= period:
        trend_adj = period + 1
    if trend_adj % 2 == 0:
        trend_adj += 1
    if trend_adj < 3:
        trend_adj = 3
    seasonal_adj = int(seasonal)

    res = STL(ts, period=period, seasonal=seasonal_adj, trend=trend_adj, robust=bool(robust)).fit()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ts.index, y=ts.values, name="observed", mode="lines"))
    fig.add_trace(go.Scatter(x=ts.index, y=res.trend, name="trend", mode="lines"))
    fig.add_trace(go.Scatter(x=ts.index, y=res.seasonal, name="seasonal", mode="lines"))
    fig.add_trace(go.Scatter(x=ts.index, y=res.resid, name="resid", mode="lines"))
    fig.update_layout(
        title=f"{title} — {area}/{group} (period={period}, trend={trend_adj}, seasonal={seasonal_adj})",
        height=520, margin=dict(l=10, r=10, t=60, b=10)
    )
    return fig


# ---------- Spectrogram (unchanged API) ----------
def spectrogram_production_plot(
    df: pd.DataFrame,
    area: str = "NO5",
    group: str = "Hydro",
    window_len: int = 24 * 7,
    overlap: float = 0.5,
    title: str = "Spectrogram — Production",
):
    ts = _series(df, area, group).astype(float)

    # Build windowed short-time energy (simple demo spectrogram)
    step = max(1, int(window_len * (1 - overlap)))
    frames = []
    times = []
    vals = ts.values
    for start in range(0, len(vals) - window_len + 1, step):
        seg = vals[start : start + window_len]
        frames.append(np.abs(np.fft.rfft(seg)))
        times.append(ts.index[start + window_len // 2])
    if not frames:
        raise ValueError("Series too short for chosen window/overlap.")

    Z = np.vstack(frames).T  # freq x time
    fig = px.imshow(
        Z,
        origin="lower",
        aspect="auto",
        labels=dict(x="window index", y="frequency bin", color="amplitude"),
        title=f"{title} — {area}/{group} (win={window_len}, overlap={overlap})",
    )
    fig.update_layout(height=520, margin=dict(l=10, r=10, t=60, b=10))
    return fig
