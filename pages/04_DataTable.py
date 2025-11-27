# --- A1 Page 2: CSV Table with LineChartColumn (with safe fallback) ---

import streamlit as st
import pandas as pd
from pathlib import Path
from lib.open_meteo import fetch_era5

st.set_page_config(page_title="Data Table", page_icon="📄", layout="wide")
st.title("📄 A1 — CSV Table with LineChartColumn")

CSV_PATH = Path("data/open-meteo-subset.csv")
CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

@st.cache_data(show_spinner=True)
def load_csv_or_make() -> pd.DataFrame:
    # 1) try the required local CSV (A1 requirement)
    if CSV_PATH.exists():
        return pd.read_csv(CSV_PATH, parse_dates=["time"])

    # 2) fall back to already-downloaded ERA5 cached on the PriceArea page (A3)
    sess = st.session_state.get("ind320_meteo_df")
    if isinstance(sess, pd.DataFrame) and "time" in sess.columns:
        df = sess.copy()
    else:
        # 3) last resort: download Bergen 2021 and create the CSV
        df = fetch_era5(lat=60.3929, lon=5.3241, year=2021)

    keep = [c for c in ["time","temperature_2m","precipitation",
                        "relative_humidity_2m","wind_speed_10m"] if c in df.columns]
    df = df[keep].copy()
    df.to_csv(CSV_PATH, index=False)
    return df

df = load_csv_or_make()
st.caption(f"Source: `{CSV_PATH}` (auto-created if missing). Cached for speed.")

# === Build table with one row per variable and a small line preview of first month ===
df["month"] = pd.to_datetime(df["time"], utc=True).dt.month
first_month = int(df["month"].min())
month_df = df[df["month"] == first_month].reset_index(drop=True)

# Only include numeric weather variables (exclude string columns like 'city', 'era5_year')
vars_ = [c for c in df.columns if c not in ("time", "month", "city", "era5_year")
         and pd.api.types.is_numeric_dtype(df[c])]
rows = [{"variable": v, "first_month": month_df[v].tolist()} for v in vars_]
table = pd.DataFrame(rows)

st.dataframe(
    table,
    column_config={
        "variable": st.column_config.TextColumn("Variable"),
        "first_month": st.column_config.LineChartColumn("First month (hourly)"),
    },
    use_container_width=True,
)
