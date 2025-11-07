# pages/06_Analysis_B.py
import streamlit as st
import numpy as np
import pandas as pd

# plotting
import plotly.express as px
import plotly.graph_objects as go

# analysis
from sklearn.neighbors import LocalOutlierFactor
from scipy.fftpack import dct

# optional: if cache not present we can fetch ERA5 here
try:
    from lib.open_meteo import fetch_era5
except Exception:
    fetch_era5 = None

st.set_page_config(page_title="Analysis B", page_icon="⚡", layout="wide")
st.title("⚡ Analysis B — SPC & LOF (Open-Meteo 2021)")

# --------------------------------------------------------------------------------------
# 0) Get city/area selection and cached ERA5 (set on page 02_PriceArea); fallback fetch
# --------------------------------------------------------------------------------------
area = st.session_state.get("ind320_area", "NO5")  # default NO5 (Bergen)
city_row = st.session_state.get("ind320_city_row")  # a small dict with {city, lat, lon, priceArea}
era5 = st.session_state.get("era5_2021")

if era5 is None:
    if city_row is None:
        st.error("No ERA5 data is cached yet. Open **02_PriceArea** first.")
        st.stop()
    # Fallback fetch (keeps the page usable if user navigates here first when running locally)
    if fetch_era5 is None:
        st.error("Helper to fetch ERA5 is unavailable. Please open **02_PriceArea** first.")
        st.stop()
    with st.spinner("Downloading ERA5 (hourly, 2021)…"):
        era5 = fetch_era5(city_row["lat"], city_row["lon"], 2021)
        st.session_state["era5_2021"] = era5

# tidy time
df = era5.copy()
if not np.issubdtype(df["time"].dtype, np.datetime64):
    df["time"] = pd.to_datetime(df["time"], utc=True)

city_label = f'{city_row["city"]} ({area}), ERA5 year: 2021' if city_row else f"{area} (ERA5 2021)"
st.caption(f"City: {city_label}")

# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def satv_highpass(series: pd.Series, cutoff: int) -> np.ndarray:
    """
    Seasonal Adjusted Temperature Variations (SATV) by high-pass DCT.
    cutoff is an index; we keep higher frequencies (>= cutoff) and zero the rest.
    """
    x = series.values.astype(float)
    x = np.nan_to_num(x, nan=np.nanmean(x))
    Xc = dct(x, norm="ortho")
    # zero low freq
    Xc[:cutoff] = 0.0
    # inverse DCT using same function (type-II/III symmetry not needed with ortho)
    # scipy.fftpack does not have idct in some hosted envs, so reconstruct manually:
    # a common workaround is to call dct again after flipping, but simplest here is:
    # we just compute an approximate inverse by applying the same transform twice;
    # however better to import idct if available:
    try:
        from scipy.fftpack import idct
        satv = idct(Xc, norm="ortho")
    except Exception:
        # very rough fallback: if idct not available
        # (kept for safety; Streamlit Cloud has idct)
        satv = dct(Xc, norm="ortho")
    return satv

def spc_bounds_from_satv(satv: np.ndarray, k_sigma: float = 3.0):
    """
    Robust SPC bounds (MAD from SATV).
    """
    med = np.median(satv)
    mad = np.median(np.abs(satv - med)) + 1e-9
    upper = med + k_sigma * mad
    lower = med - k_sigma * mad
    return lower, upper, mad

def lof_flags(y: np.ndarray, contamination: float = 0.01, n_neighbors: int = 20):
    """
    Local Outlier Factor flags (True=anomaly) for a 1-D series.
    """
    X = y.reshape(-1, 1)
    lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=contamination)
    labels = lof.fit_predict(X)  # -1 is outlier
    return labels == -1

# --------------------------------------------------------------------------------------
# UI with tabs: SPC (Temperature) and LOF (Precipitation)
# --------------------------------------------------------------------------------------
tab_spc, tab_lof = st.tabs(["SPC (Temperature)", "Anomaly: LOF (Precipitation)"])

with tab_spc:
    st.subheader("Temperature with SPC outliers")
    col1, col2 = st.columns(2)
    with col1:
        cutoff = st.slider("DCT high-pass cutoff (keep high frequencies ≥ this index)", 10, 80, 30, step=2)
    with col2:
        k_sigma = st.slider("SPC threshold (k × MAD)", 2.0, 5.0, 3.0, step=0.25)

    # compute SATV & bounds
    satv = satv_highpass(df["temperature_2m"], cutoff)
    lower, upper, mad = spc_bounds_from_satv(satv, k_sigma)
    # mark outliers against bounds (on SATV)
    is_outlier = (satv > upper) | (satv < lower)
    ts = df[["time", "temperature_2m"]].copy()
    ts["is_outlier"] = is_outlier

    # --- clean, minimal plot: grey line + red markers for outliers + dashed bounds ---
    fig = px.line(
        ts, x="time", y="temperature_2m",
        title=f"Temperature with SPC outliers (k={k_sigma:.2f}, cutoff={cutoff})",
    )
    # outliers
    outs = ts[ts["is_outlier"]]
    fig.add_scatter(
        x=outs["time"], y=outs["temperature_2m"],
        mode="markers", name="Outlier",
        marker=dict(size=6, color="#FF4B4B", opacity=0.95),
    )
    # SPC bounds (as constant lines across the chart range)
    fig.add_hline(y=upper, line=dict(color="#D62728", width=1.5, dash="dot"), annotation_text="SPC upper", annotation_position="top left")
    fig.add_hline(y=lower, line=dict(color="#D62728", width=1.5, dash="dot"), annotation_text="SPC lower", annotation_position="bottom left")

    # polish
    fig.update_traces(line=dict(color="#9AA0A6", width=1.2), selector=dict(mode="lines"))
    fig.update_layout(
        xaxis_title="time",
        yaxis_title="Temperature (°C)",
        legend_title="Legend",
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        font=dict(color="white"),
        hovermode="x unified",
        margin=dict(l=40, r=20, t=60, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

    # summary
    n_out = int(is_outlier.sum())
    st.caption(f"Outliers: **{n_out} / {len(ts)}** ({100*n_out/len(ts):.2f}%).  MAD = **{mad:.3f}**")

with tab_lof:
    st.subheader("Precipitation — Local Outlier Factor (LOF)")
    c1, c2 = st.columns(2)
    with c1:
        contamination = st.slider("Proportion of anomalies", 0.002, 0.05, 0.01, step=0.002, format="%.3f")
    with c2:
        n_neighbors = st.slider("LOF neighbors", 10, 50, 20, step=2)

    y = df["precipitation"].astype(float).values
    flags = lof_flags(y, contamination=contamination, n_neighbors=n_neighbors)

    lof_df = df[["time", "precipitation"]].copy()
    lof_df["is_anomaly"] = flags

    # Clear visualization: line for precip + red anomaly markers
    fig2 = px.line(
        lof_df, x="time", y="precipitation",
        title=f"Precipitation with LOF anomalies (contamination={contamination:.3f}, n_neighbors={n_neighbors})",
    )
    anomalies = lof_df[lof_df["is_anomaly"]]
    fig2.add_scatter(
        x=anomalies["time"], y=anomalies["precipitation"],
        mode="markers", name="Anomaly",
        marker=dict(size=6, color="#FF4B4B", opacity=0.95),
    )
    fig2.update_traces(line=dict(color="#8AB4F8", width=1.3), selector=dict(mode="lines"))
    fig2.update_layout(
        xaxis_title="time",
        yaxis_title="Precipitation (mm)",
        legend_title="Legend",
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        font=dict(color="white"),
        hovermode="x unified",
        margin=dict(l=40, r=20, t=60, b=40),
    )
    st.plotly_chart(fig2, use_container_width=True)

    n_anom = int(flags.sum())
    st.caption(f"Anomalies: **{n_anom} / {len(lof_df)}** ({100*n_anom/len(lof_df):.2f}%).")
