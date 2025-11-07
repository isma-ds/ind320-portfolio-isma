# pages/06_Analysis_B.py
# ---------------------------------
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.neighbors import LocalOutlierFactor
from scipy.fft import dct, idct
import plotly.express as px

from lib.open_meteo import get_or_fetch_era5

st.set_page_config(page_title="Analysis B", page_icon="⚡", layout="wide")
st.title("⚡ Analysis B — SPC & LOF (Open-Meteo 2021)")

# ---- Read area/city from session or use defaults (NO5 Bergen) ----
area = st.session_state.get("ind320_area", "NO5")
city = st.session_state.get("ind320_city", "Bergen")
lat  = float(st.session_state.get("ind320_lat", 60.3929))
lon  = float(st.session_state.get("ind320_lon", 5.3241))
year = 2021

# ---- Fetch ERA5 if missing (so page works on cold start) ----
try:
    df = get_or_fetch_era5(st, area, lat, lon, year)
except Exception as e:
    st.error(f"Could not fetch ERA5: {e}")
    st.stop()

# ============ UI ============

tab1, tab2 = st.tabs(["Temperature — SPC (DCT high-pass)", "Precipitation — LOF anomalies"])

with tab1:
    col1, col2 = st.columns([1,1])
    with col1:
        cutoff = st.slider("DCT high-pass cutoff (keep high frequencies ≥ this index)",
                           min_value=8, max_value=200, value=30, step=2,
                           help="Higher = more aggressive seasonal removal")
    with col2:
        k_sigma = st.slider("SPC threshold (k × MAD)", min_value=2.0, max_value=6.0,
                            value=3.0, step=0.5)

    # Build SATV: temperature_2m seasonal-adjusted via DCT high-pass
    ts = df[["time", "temperature_2m"]].dropna().copy()
    x = ts["temperature_2m"].to_numpy(dtype=float)

    # DCT / inverse DCT to remove low-frequency seasonal component
    X = dct(x, norm="ortho")
    X[:cutoff] = 0.0
    satv = idct(X, norm="ortho")

    ts["SATV"] = satv

    # Robust SPC bounds using MAD
    med = np.median(satv)
    mad = np.median(np.abs(satv - med)) or 1e-9
    upper = med + k_sigma * 1.4826 * mad
    lower = med - k_sigma * 1.4826 * mad
    ts["is_outlier"] = (ts["SATV"] > upper) | (ts["SATV"] < lower)

    st.caption(f"City: **{city} ({area})**, ERA5 year: **{year}**")
    fig = px.scatter(
        ts, x="time", y="temperature_2m", color="is_outlier",
        color_discrete_map={False: "#AAAAAA", True: "#FF4B4B"},
        title=f"Temperature with SPC outliers (k={k_sigma}, cutoff={cutoff})"
    )
    # Show bounds as lines of SATV but do not plot SATV itself (assignment wording)
    bounds_df = pd.DataFrame({
        "time": ts["time"],
        "upper": upper,
        "lower": lower
    })
    fig.add_scatter(x=bounds_df["time"], y=bounds_df["upper"], mode="lines", name="SPC upper")
    fig.add_scatter(x=bounds_df["time"], y=bounds_df["lower"], mode="lines", name="SPC lower")
    st.plotly_chart(fig, use_container_width=True)

    st.write(
        f"Outliers: **{int(ts['is_outlier'].sum())}** / {len(ts)} "
        f"({100*ts['is_outlier'].mean():.2f}%).  "
        f"MAD={mad:.3f}"
    )

with tab2:
    contamination = st.slider("LOF expected anomaly proportion", 0.001, 0.05, 0.01, 0.001)
    n_neighbors = st.slider("LOF neighbors", 5, 50, 20, 1)

    dfp = df[["time", "precipitation"]].fillna(0.0).copy()
    X = dfp[["precipitation"]].to_numpy(dtype=float)

    lof = LocalOutlierFactor(
        n_neighbors=n_neighbors,
        contamination=contamination,
        novelty=False
    )
    labels = lof.fit_predict(X)  # -1 = outlier
    dfp["is_outlier"] = (labels == -1)

    figp = px.scatter(
        dfp, x="time", y="precipitation", color="is_outlier",
        color_discrete_map={False: "#AAAAAA", True: "#FF4B4B"},
        title=f"LOF precipitation anomalies (contam={contamination}, neighbors={n_neighbors})"
    )
    st.plotly_chart(figp, use_container_width=True)

    st.write(
        f"Anomalies: **{int(dfp['is_outlier'].sum())}** / {len(dfp)} "
        f"({100*dfp['is_outlier'].mean():.2f}%)."
    )
