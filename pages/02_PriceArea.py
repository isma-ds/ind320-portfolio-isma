# pages/02_PriceArea.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from datetime import datetime

st.set_page_config(page_title="Price Area Dashboard", page_icon="⚡", layout="wide")
st.title("⚡ Price Area Dashboard (Elhub demo + Open-Meteo 2021)")

DATA_PATH = "data/open-meteo-subset.csv"

# ------------- Helper: Load or auto-generate ERA5 demo data -------------
@st.cache_data
def load_era5_data():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH, parse_dates=["time"])
        st.info("✅ Using cached ERA5 data from local file.")
    else:
        st.warning("No cached ERA5 file found. Creating demo dataset...")
        # --- Demo fallback: create hourly data for Bergen 2021
        date_rng = pd.date_range("2021-01-01", "2021-12-31 23:00", freq="H")
        np.random.seed(0)
        temp = 5 + 10 * np.sin(2 * np.pi * date_rng.dayofyear / 365) + np.random.normal(0, 2, len(date_rng))
        df = pd.DataFrame({
            "time": date_rng,
            "temperature_2m": temp,
            "city": "Bergen",
            "era5_year": 2021
        })
        os.makedirs("data", exist_ok=True)
        df.to_csv(DATA_PATH, index=False)
        st.success("✅ ERA5 dataset created and cached at data/open-meteo-subset.csv")
    return df

# load automatically
era5_df = load_era5_data()

# ------------- Elhub demo data (for energy production visualization) -------------
@st.cache_data
def load_elhub_demo():
    df = pd.DataFrame({
        "priceArea": np.repeat(["NO1", "NO2", "NO3", "NO4", "NO5"], 12),
        "month": list(range(1, 13)) * 5,
        "Hydro": np.random.randint(3000, 8000, 60),
        "Wind": np.random.randint(2000, 6000, 60),
        "Thermal": np.random.randint(500, 1500, 60),
    })
    return df

elhub_df = load_elhub_demo()

# ------------- User controls -------------
st.subheader("Select price area")
area = st.radio("", ["NO1", "NO2", "NO3", "NO4", "NO5"], index=4, horizontal=True)

st.subheader("Production groups")
groups = st.multiselect("Select production groups", ["Hydro", "Wind", "Thermal"], default=["Hydro", "Wind"])

st.subheader("Month")
month = st.selectbox("Select month", list(range(1, 13)), index=1)

# ------------- Visuals -------------
df_area = elhub_df[elhub_df["priceArea"] == area]

# pie chart of total production
totals = df_area[groups].sum().reset_index()
totals.columns = ["Group", "Production"]
fig_pie = px.pie(totals, names="Group", values="Production", title=f"Total production in 2021 — {area}")
st.plotly_chart(fig_pie, use_container_width=True)

# line chart of hourly production pattern (simplified demo)
df_line = pd.DataFrame({
    "time": pd.date_range(f"2021-{month:02d}-01", periods=720, freq="H"),
})
for g in groups:
    df_line[g] = np.random.randint(2000, 7000, len(df_line))
df_line = df_line.melt(id_vars="time", var_name="productionGroup", value_name="quantitykWh")

fig_line = px.line(
    df_line,
    x="time",
    y="quantitykWh",
    color="productionGroup",
    title=f"Hourly production — {area}, month={month}"
)
st.plotly_chart(fig_line, use_container_width=True)

# ------------- Footer / Data Source -------------
with st.expander("📂 Data source"):
    st.write("""
    - **ERA5/Open-Meteo 2021** demo dataset: cached in `data/open-meteo-subset.csv`  
    - **Elhub simulated data** for price area production (Hydro, Wind, Thermal)
    """)
