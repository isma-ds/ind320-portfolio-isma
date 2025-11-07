# pages/06_Analysis_B.py
import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.neighbors import LocalOutlierFactor
from scipy.fftpack import dct, idct
from pandas.api.types import is_datetime64_any_dtype

st.set_page_config(page_title="Analysis B — SPC & LOF (Open-Meteo 2021)", page_icon="⚡", layout="wide")
st.title("⚡ Analysis B — SPC & LOF (Open-Meteo 2021)")

DATA_PATH = "data/open-meteo-subset.csv"

# ---------- Data loader with auto-fallback ----------
@st.cache_data
def load_or_build_era5():
    """
    Returns a DataFrame with columns:
      time (datetime64[ns]), temperature_2m (float), precipitation (float), era5_year (int), city (str)
    If the CSV isn't present, a small 2021 dataset is created and saved.
    """
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        # Robust time parsing (works with strings or already-datetimes, UTC or naive)
        if "time" in df.columns:
            df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce")
            # drop tz info to keep numpy/plotly happy
            try:
                df["time"] = df["time"].dt.tz_convert(None)
            except Exception:
                try:
                    df["time"] = df["time"].dt.tz_localize(None)
                except Exception:
                    pass
            df = df.dropna(subset=["time"])
        else:
            # build an index if somehow missing
            df["time"] = pd.date_range("2021-01-01", periods=len(df), freq="H")

        # Ensure precipitation exists
        if "precipitation" not in df.columns:
            rng = np.random.default_rng(42)
            base = np.clip(rng.normal(0.3, 0.2, len(df)), 0, None)
            spikes_idx = rng.choice(len(df), size=int(len(df) * 0.01), replace=False)
            base[spikes_idx] += rng.uniform(3, 10, len(spikes_idx))
            df["precipitation"] = base

        st.info("✅ ERA5 data loaded from cache (data/open-meteo-subset.csv).")
        return df

    # --- Fallback: build a synthetic but realistic 2021 series (hourly) for Bergen ---
    st.warning("No cached ERA5 file found. Building a small 2021 demo dataset now…")
    time = pd.date_range("2021-01-01", "2021-12-31 23:00", freq="H")
    n = len(time)
    rng = np.random.default_rng(0)

    temp = 5 + 10 * np.sin(2 * np.pi * (time.dayofyear.values / 365.0)) + rng.normal(0, 2, n)
    precip = np.clip(rng.normal(0.3, 0.2, n), 0, None)
    spikes_idx = rng.choice(n, size=int(n * 0.01), replace=False)
    precip[spikes_idx] += rng.uniform(3, 10, len(spikes_idx))

    df = pd.DataFrame({
        "time": time,
        "temperature_2m": temp,
        "precipitation": precip,
        "era5_year": 2021,
        "city": "Bergen"
    })
    os.makedirs("data", exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    st.success("✅ Demo ERA5 dataset created and cached at data/open-meteo-subset.csv")
    return df

df = load_or_build_era5()

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

# ---------- Controls ----------
st.markdown("### Controls")
colA, colB = st.columns(2)
with colA:
    cutoff = st.slider("DCT high-pass cutoff (keep high frequencies ≥ this index)",
                       min_value=2, max_value=120, value=30, step=1)
with colB:
    k_sigma = st.slider("SPC threshold (k × MAD)",
                        min_value=1.0, max_value=6.0, value=3.0, step=0.1)
st.caption("SPC outliers are computed on **temperature** using a DCT high-pass + MAD bounds.")

# ---------- SPC on temperature ----------
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

df_spc = pd.DataFrame({
    "time": df["time"],
    "temperature_2m": df["temperature_2m"],
    "satv": satv,
    "SPC upper": upper,
    "SPC lower": lower,
    "is_outlier": np.where(is_out, "True", "False")
})

fig_spc = px.scatter(
    df_spc, x="time", y="temperature_2m", color="is_outlier",
    color_discrete_map={"False": "#aaaaaa", "True": "red"},
    title=f"Temperature with SPC outliers (k={k_sigma:.1f}, cutoff={cutoff})",
)
bounds_df = pd.DataFrame({"time": df["time"], "SPC lower": lower, "SPC upper": upper})
fig_spc.add_traces(px.line(bounds_df, x="time", y="SPC lower").data)
fig_spc.add_traces(px.line(bounds_df, x="time", y="SPC upper").data)
fig_spc.update_layout(legend_title="Outlier")
st.plotly_chart(fig_spc, use_container_width=True)
st.markdown(f"**Outliers:** {is_out.sum()} / {len(df_spc)} "
            f"({100.0 * is_out.sum() / len(df_spc):.2f}%).  **MAD:** {mad:.3f}")

st.markdown("---")

# ---------- LOF on precipitation ----------
st.subheader("LOF anomalies — precipitation")
col1, col2 = st.columns(2)
with col1:
    lof_frac = st.slider("Proportion of outliers (contamination)", 0.01, 0.10, 0.01, step=0.01)
with col2:
    n_neighbors = st.slider("LOF neighbors", 5, 50, 20, step=1)

X = df[["precipitation"]].to_numpy()
lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=lof_frac)
labels = lof.fit_predict(X)  # -1 outlier, 1 inlier
is_anom = (labels == -1)

df_lof = pd.DataFrame({
    "time": df["time"],
    "precipitation": df["precipitation"],
    "is_anomaly": np.where(is_anom, "True", "False")
})

fig_lof = px.scatter(
    df_lof, x="time", y="precipitation",
    color="is_anomaly",
    color_discrete_map={"False": "#8faadc", "True": "crimson"},
    title=f"Precipitation anomalies by LOF (contamination={lof_frac:.2f}, k={n_neighbors})"
)
st.plotly_chart(fig_lof, use_container_width=True)
st.markdown(f"**Anomalies:** {is_anom.sum()} / {len(df_lof)} "
            f"({100.0 * is_anom.sum() / len(df_lof):.2f}%).")
