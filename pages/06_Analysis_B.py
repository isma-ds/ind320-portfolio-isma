import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# Optional DCT (preferred). If SciPy isn't available on Cloud, we fall back to FFT.
try:
    from scipy.fftpack import dct, idct
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False

from sklearn.neighbors import LocalOutlierFactor

st.set_page_config(page_title="Analysis B — SPC & LOF (Open-Meteo 2021)", layout="wide")
st.title("⚡ Analysis B — SPC & LOF (Open-Meteo 2021)")

# ---------- 1) Get ERA5 data from session (set on PriceArea page) ----------
df = None
for key in ("era5_df", "open_meteo_df", "era5_cache"):
    if key in st.session_state and isinstance(st.session_state[key], pd.DataFrame):
        df = st.session_state[key].copy()
        break

if df is None:
    st.error("No ERA5 data is cached yet. Open **PriceArea** first so it can download 2021 data.")
    st.stop()

# ---------- 2) Normalize columns & coerce dtypes ----------
# Expect at least: time, temperature_2m, precipitation (names from Open-Meteo ERA5)
rename_map = {
    "Time": "time",
    "timestamp": "time",
    "temp": "temperature_2m",
    "temperature": "temperature_2m",
    "precip": "precipitation",
    "rain": "precipitation",
}
df = df.rename(columns={c: rename_map.get(c, c) for c in df.columns})

# Ensure time is real datetime (this line fixes your TypeError)
df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce")
df = df.dropna(subset=["time"]).sort_values("time").reset_index(drop=True)

# Safety: create missing columns if API subset differed
if "temperature_2m" not in df.columns:
    st.error("Column `temperature_2m` was not found in ERA5 dataframe.")
    st.stop()
if "precipitation" not in df.columns:
    # If precipitation missing, fabricate zeros so LOF tab still runs
    df["precipitation"] = 0.0

# ---------- Small helpers ----------
def spc_mad_bounds(x: np.ndarray, k: float = 3.0):
    """Robust SPC bounds using median ± k * 1.4826 * MAD."""
    med = np.median(x)
    mad = np.median(np.abs(x - med))
    sigma = 1.4826 * mad
    upper = med + k * sigma
    lower = med - k * sigma
    return lower, upper, med, mad, sigma

def dct_highpass(x: np.ndarray, cutoff: int) -> np.ndarray:
    """
    High-pass using DCT (preferred). Keep only high frequencies (>= cutoff),
    then invert. If SciPy is unavailable, fall back to FFT.
    """
    n = len(x)
    if n == 0:
        return x

    if HAVE_SCIPY:
        X = dct(x, norm="ortho")
        # Zero out low frequencies below cutoff
        cutoff_idx = int(cutoff)
        cutoff_idx = max(0, min(cutoff_idx, n - 1))
        X[:cutoff_idx] = 0.0
        x_hp = idct(X, norm="ortho")
        return x_hp
    else:
        # FFT fallback (not exactly DCT but acceptable if SciPy is missing)
        X = np.fft.rfft(x)
        # Roughly map cutoff to rfft bins
        bins = len(X)
        cutoff_idx = int(np.clip(cutoff, 0, bins - 1))
        X[:cutoff_idx] = 0.0
        x_hp = np.fft.irfft(X, n=len(x))
        return x_hp

# ---------- 3) UI controls ----------
st.subheader("Temperature outliers (SPC on DCT high-pass)")
c1, c2 = st.columns([1, 1])
cutoff = c1.slider("DCT high-pass cutoff (keep high frequencies ≥ this index)", 10, 200, 30, 1)
k_sigma = c2.slider("SPC threshold (k × MAD)", 1.0, 6.0, 3.0, 0.25)

# ---------- 4) SATV via DCT high-pass ----------
temp = df["temperature_2m"].astype(float).to_numpy()
satv = dct_highpass(temp, cutoff=cutoff)

# SPC on SATV (but we *plot* original temperature)
low, up, med, mad, sigma = spc_mad_bounds(satv, k=k_sigma)
is_out = (satv > up) | (satv < low)

df_spc = pd.DataFrame(
    {
        "time": df["time"],
        "temperature_2m": temp,
        "SATV": satv,
        "is_outlier": np.where(is_out, "True", "False"),
        "SPC upper": up,
        "SPC lower": low,
    }
)

fig_spc = px.line(
    df_spc,
    x="time",
    y="temperature_2m",
    title=f"Temperature with SPC outliers (k={k_sigma:.2f}, cutoff={cutoff})",
)
# Add robust bounds
fig_spc.add_scatter(x=df_spc["time"], y=df_spc["SPC upper"], mode="lines", name="SPC upper")
fig_spc.add_scatter(x=df_spc["time"], y=df_spc["SPC lower"], mode="lines", name="SPC lower")
# Overlay outliers
out_pts = df_spc[is_out]
fig_spc.add_scatter(
    x=out_pts["time"],
    y=out_pts["temperature_2m"],
    mode="markers",
    name="Outliers",
)

fig_spc.update_layout(
    plot_bgcolor="#0E1117",
    paper_bgcolor="#0E1117",
    font=dict(color="white"),
    hovermode="x unified",
    margin=dict(l=40, r=20, t=60, b=40),
    legend_title=None,
)
st.plotly_chart(fig_spc, use_container_width=True)
st.caption(
    f"Outliers: {is_out.sum()} / {len(df_spc)} "
    f"({(100*is_out.mean()):.2f}%). MAD={mad:.3f}"
)

# ---------- 5) Precipitation anomalies with LOF ----------
st.subheader("Precipitation anomalies (Local Outlier Factor)")
c3, c4 = st.columns([1, 1])
cont = c3.slider("Proportion of outliers (LOF contamination)", 0.001, 0.05, 0.01, 0.001)
n_neighbors = c4.slider("LOF neighbors", 5, 50, 20, 1)

prec = df["precipitation"].astype(float).to_numpy().reshape(-1, 1)
# LOF: y = -1 for outlier, 1 for inlier
lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=cont)
labels = lof.fit_predict(prec)
is_anom = labels == -1

df_lof = pd.DataFrame(
    {"time": df["time"], "precipitation": df["precipitation"].astype(float), "anomaly": is_anom}
)

fig_lof = px.line(
    df_lof,
    x="time",
    y="precipitation",
    title=f"Precipitation with LOF anomalies (cont={cont:.3f}, k={n_neighbors})",
)
anom_pts = df_lof[df_lof["anomaly"]]
fig_lof.add_scatter(
    x=anom_pts["time"],
    y=anom_pts["precipitation"],
    mode="markers",
    name="Anomaly",
)

fig_lof.update_layout(
    plot_bgcolor="#0E1117",
    paper_bgcolor="#0E1117",
    font=dict(color="white"),
    hovermode="x unified",
    margin=dict(l=40, r=20, t=60, b=40),
    legend_title=None,
)
st.plotly_chart(fig_lof, use_container_width=True)
st.caption(f"Anomalies: {is_anom.sum()} / {len(df_lof)} ({(100*is_anom.mean()):.2f}%).")
