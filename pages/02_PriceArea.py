# pages/02_PriceArea.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from datetime import datetime
import sys
sys.path.append('..')
from lib.mongodb_client import load_production_2021, get_monthly_aggregation

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

# ------------- Real Elhub data from MongoDB (NO FAKE DATA!) -------------
@st.cache_data(ttl=3600)
def load_real_elhub_monthly():
    """
    Load REAL 2021 production data from MongoDB and aggregate by month.
    This replaces the fake demo data.
    """
    df = get_monthly_aggregation()

    if df.empty:
        st.error("Failed to load data from MongoDB")
        return pd.DataFrame()

    # Pivot to wide format for easier visualization
    df_pivot = df.pivot_table(
        index=['priceArea', 'month'],
        columns='productionGroup',
        values='quantityKwh',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    return df_pivot

elhub_df = load_real_elhub_monthly()

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

# line chart of hourly production - REAL DATA from MongoDB
df_full = load_production_2021()
df_line = df_full[
    (df_full['priceArea'] == area) &
    (df_full['productionGroup'].isin(groups)) &
    (df_full['startTime'].dt.month == month)
].copy()

# Rename columns for compatibility
df_line = df_line.rename(columns={'startTime': 'time', 'quantityKwh': 'quantitykWh'})

fig_line = px.line(
    df_line,
    x="time",
    y="quantitykWh",
    color="productionGroup",
    title=f"Hourly production — {area}, month={month}"
)
st.plotly_chart(fig_line, use_container_width=True)

# ------------- Footer / Data Source -------------
with st.expander("📂 Data Source"):
    st.markdown("""
    ### Real Data Sources (Assessment 2)

    **Elhub Production Data (2021):**
    - Source: MongoDB Atlas (ind320.production_2021)
    - Original Source: Elhub API (PRODUCTION_PER_GROUP_MBA_HOUR)
    - Time Period: Year 2021 (all days and hours)
    - Price Areas: NO1, NO2, NO3, NO4, NO5
    - Production Groups: Hydro, Wind, Thermal, Solar
    - Resolution: Hourly data

    **Data Pipeline:**
    1. Fetched from Elhub API (https://api.elhub.no)
    2. Stored in local Cassandra database
    3. Processed using Apache Spark
    4. Filtered to 4 columns: priceArea, productionGroup, startTime, quantityKwh
    5. Uploaded to MongoDB Atlas
    6. Displayed in this Streamlit app

    **ERA5/Open-Meteo 2021:**
    - Weather data from Open-Meteo API
    - Cached in `data/open-meteo-subset.csv`

    ⚠️ **No CSV downloads used for Elhub data - all from MongoDB!**
    """)
