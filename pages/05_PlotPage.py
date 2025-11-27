# --- A1 Page 3: Plot page (column picker + month selector) with safe fallback ---

import streamlit as st
import pandas as pd
from pathlib import Path
from lib.open_meteo import fetch_era5

st.set_page_config(page_title="Plot", page_icon="📈", layout="wide")
st.title("📈 A1 — Plot with selectors")

CSV_PATH = Path("data/open-meteo-subset.csv")
CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

@st.cache_data(show_spinner=True)
def load_csv_or_make() -> pd.DataFrame:
    if CSV_PATH.exists():
        return pd.read_csv(CSV_PATH, parse_dates=["time"])

    sess = st.session_state.get("ind320_meteo_df")
    if isinstance(sess, pd.DataFrame) and "time" in sess.columns:
        df = sess.copy()
    else:
        df = fetch_era5(lat=60.3929, lon=5.3241, year=2021)  # Bergen 2021

    keep = [c for c in ["time","temperature_2m","precipitation",
                        "relative_humidity_2m","wind_speed_10m"] if c in df.columns]
    df = df[keep].copy()
    df.to_csv(CSV_PATH, index=False)
    return df

df = load_csv_or_make()
df["time"] = pd.to_datetime(df["time"], utc=True)
df["month"] = df["time"].dt.month

# === Controls per spec ===
# Only include numeric columns (exclude string columns like 'city', 'era5_year')
cols = [c for c in df.columns if c not in ("time", "month", "city", "era5_year")
        and pd.api.types.is_numeric_dtype(df[c])]
choice = st.selectbox("Choose a column (or All)", ["All"] + cols, index=0)

months_sorted = sorted(df["month"].unique())
default_month = months_sorted[0] if months_sorted else 1
m = st.select_slider("Select a month", options=months_sorted, value=default_month)

# === Plot ===
plot_df = df[df["month"] == m].set_index("time")

if choice == "All":
    st.line_chart(plot_df[cols], use_container_width=True)
else:
    st.line_chart(plot_df[[choice]], use_container_width=True)

st.caption(f"Data: `{CSV_PATH}` (cached & auto-created if missing). Default shows the first month.")
