# pages/06_Analysis_B.py
import sys
sys.path.append('..')
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.neighbors import LocalOutlierFactor
from scipy.fftpack import dct, idct
from pandas.api.types import is_datetime64_any_dtype
from lib.open_meteo import fetch_era5

st.set_page_config(page_title="Analysis B — SPC & LOF (Real ERA5)", page_icon="⚡", layout="wide")
st.title("⚡ Analysis B — SPC & LOF Outlier Detection (Real ERA5 Data)")

# ---------- Load REAL ERA5 data from Open-Meteo API ----------
@st.cache_data(ttl=3600)
def load_real_era5():
    """
    Fetch REAL ERA5 weather data from Open-Meteo API for Bergen, Norway (2021).
    Returns DataFrame with: time, temperature_2m, precipitation, and other weather variables.
    """
    try:
        with st.spinner("Fetching real ERA5 weather data from Open-Meteo API..."):
            # Bergen, Norway coordinates
            df = fetch_era5(lat=60.39, lon=5.32, year=2021,
                          hourly_vars=["temperature_2m", "precipitation", "relative_humidity_2m", "wind_speed_10m"])
            df['era5_year'] = 2021
            df['city'] = 'Bergen'

            # Remove timezone for compatibility with numpy/plotly
            df['time'] = df['time'].dt.tz_localize(None)

        st.success("✅ Real ERA5 data loaded from Open-Meteo API (8,760 hourly records)")
        return df
    except Exception as e:
        st.error(f"Failed to fetch ERA5 data from API: {e}")
        st.warning("Please check your internet connection and try again.")
        return pd.DataFrame()

df = load_real_era5()

if df.empty:
    st.error("No data available. Cannot proceed with analysis.")
    st.stop()

# Safety: ensure datetime (naive)
if not is_datetime64_any_dtype(df["time"]):
    df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce")
try:
    df["time"] = df["time"].dt.tz_convert(None)
except Exception:
    try:
        df["time"] = df["time"].dt.tz_localize(None)
    except Exception:
        pass
df = df.dropna(subset=["time"])

# ---------- Create Tabs for SPC and LOF ----------
tabs = st.tabs(["🌡️ Temperature Outliers (SPC)", "🌧️ Precipitation Anomalies (LOF)"])

# ========== TAB 1: SPC (Temperature Outliers) ==========
with tabs[0]:
    st.markdown("### Temperature Outlier Detection using DCT + SPC")
    st.markdown("""
    This analysis uses **Direct Cosine Transform (DCT)** for high-pass filtering to create 
    Seasonally Adjusted Temperature Variations (SATV), then applies **Statistical Process Control (SPC)** 
    with robust statistics (median + MAD) to identify outliers.
    """)
    
    # Controls
    colA, colB = st.columns(2)
    with colA:
        cutoff = st.slider("DCT high-pass cutoff (keep high frequencies ≥ this index)",
                           min_value=2, max_value=120, value=30, step=1, key="spc_cutoff")
    with colB:
        k_sigma = st.slider("SPC threshold (k × MAD)",
                            min_value=1.0, max_value=6.0, value=3.0, step=0.1, key="spc_sigma")
    
    # SPC Analysis
    y = df["temperature_2m"].to_numpy()
    Y = dct(y, type=2, norm="ortho")
    cut = np.clip(cutoff, 0, len(Y) - 1)
    Y[:cut] = 0.0
    satv = idct(Y, type=2, norm="ortho")
    
    med = np.median(satv)
    mad = np.median(np.abs(satv - med))
    sigma = 1.4826 * mad if mad > 0 else np.std(satv)
    upper = k_sigma * sigma
    lower = -k_sigma * sigma
    is_out = (satv > upper) | (satv < lower)
    
    # Calculate Trend (Original - SATV) to plot boundaries on the original scale
    trend = y - satv
    upper_boundary = trend + upper
    lower_boundary = trend + lower

    df_spc = pd.DataFrame({
        "time": df["time"],
        "temperature_2m": df["temperature_2m"],
        "satv": satv,
        "trend": trend,
        "SPC upper": upper_boundary,
        "SPC lower": lower_boundary,
        "is_outlier": np.where(is_out, "True", "False")
    })

    # Plot
    fig_spc = px.scatter(
        df_spc, x="time", y="temperature_2m", color="is_outlier",
        color_discrete_map={"False": "#aaaaaa", "True": "red"},
        title=f"Temperature with SPC outliers (k={k_sigma:.1f}, cutoff={cutoff})",
    )
    # FIXED: Boundaries now follow the temperature curve (professor feedback fix)
    # Using the correct formula: trend = temp - satv, boundaries = trend + limits
    bounds_df = pd.DataFrame({
        "time": df["time"],
        "SPC lower": lower_boundary,
        "SPC upper": upper_boundary
    })
    fig_spc.add_traces(px.line(bounds_df, x="time", y="SPC lower").data)
    fig_spc.add_traces(px.line(bounds_df, x="time", y="SPC upper").data)
    fig_spc.update_layout(legend_title="Outlier")
    st.plotly_chart(fig_spc, use_container_width=True)
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Outliers", f"{is_out.sum():,}")
    with col2:
        st.metric("Outlier Percentage", f"{100.0 * is_out.sum() / len(df_spc):.2f}%")
    with col3:
        st.metric("MAD (Robust Std)", f"{mad:.3f}")
    
    # Expander with details
    with st.expander("📊 View Outlier Details"):
        outlier_df = df_spc[df_spc["is_outlier"] == "True"][["time", "temperature_2m", "satv"]]
        st.dataframe(outlier_df, use_container_width=True)

# ========== TAB 2: LOF (Precipitation Anomalies) ==========
with tabs[1]:
    st.markdown("### Precipitation Anomaly Detection using LOF")
    st.markdown("""
    This analysis uses **Local Outlier Factor (LOF)** to identify precipitation anomalies 
    based on local density deviation. Points with significantly lower density than their 
    neighbors are flagged as anomalies.
    """)
    
    # Controls
    col1, col2 = st.columns(2)
    with col1:
        lof_frac = st.slider("Proportion of outliers (contamination)", 
                             0.01, 0.10, 0.01, step=0.01, key="lof_contamination")
    with col2:
        n_neighbors = st.slider("LOF neighbors", 5, 50, 20, step=1, key="lof_neighbors")
    
    # LOF Analysis
    X = df[["precipitation"]].to_numpy()
    lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=lof_frac)
    labels = lof.fit_predict(X)  # -1 outlier, 1 inlier
    is_anom = (labels == -1)
    
    df_lof = pd.DataFrame({
        "time": df["time"],
        "precipitation": df["precipitation"],
        "is_anomaly": np.where(is_anom, "True", "False")
    })
    
    # Plot
    fig_lof = px.scatter(
        df_lof, x="time", y="precipitation",
        color="is_anomaly",
        color_discrete_map={"False": "#8faadc", "True": "crimson"},
        title=f"Precipitation anomalies by LOF (contamination={lof_frac:.2f}, k={n_neighbors})"
    )
    st.plotly_chart(fig_lof, use_container_width=True)
    
    # Statistics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Anomalies", f"{is_anom.sum():,}")
    with col2:
        st.metric("Anomaly Percentage", f"{100.0 * is_anom.sum() / len(df_lof):.2f}%")
    
    # Expander with details
    with st.expander("📊 View Anomaly Details"):
        anomaly_df = df_lof[df_lof["is_anomaly"] == "True"][["time", "precipitation"]]
        st.dataframe(anomaly_df, use_container_width=True)

# ---------- Data Source Documentation ----------
with st.expander("📂 Data Source"):
    st.markdown("""
    ### Weather Data (Open-Meteo ERA5)
    
    **Source**: Open-Meteo API (https://open-meteo.com)  
    **Model**: ERA5 Historical Reanalysis  
    **Year**: 2021  
    **Location**: Bergen, Norway (or selected city)  
    **Resolution**: Hourly data  
    **Variables**: Temperature (2m), Precipitation  
    
    **Analysis Methods**:
    - **DCT (Direct Cosine Transform)**: Frequency-domain filtering to remove seasonal trends
    - **SPC (Statistical Process Control)**: Robust outlier detection using median + MAD
    - **LOF (Local Outlier Factor)**: Density-based anomaly detection
    
    **Note**: Data is cached locally at `data/open-meteo-subset.csv` for performance.
    """)
