# pages/02_PriceArea.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import sys
sys.path.append('..')
from lib.mongodb_client import load_production_2021, get_monthly_aggregation
from lib.open_meteo import fetch_era5

st.set_page_config(page_title="Price Area Dashboard", page_icon="⚡", layout="wide")
st.title("⚡ Price Area Dashboard (Real Elhub + Open-Meteo ERA5)")

# ------------- Load REAL ERA5 data from Open-Meteo API -------------
@st.cache_data(ttl=3600)
def load_era5_data():
    """
    Fetch REAL ERA5 weather data from Open-Meteo API for Bergen, Norway (2021).
    No demo data - this is actual historical weather reanalysis.
    """
    try:
        with st.spinner("Fetching real ERA5 weather data from Open-Meteo API..."):
            # Bergen coordinates
            df = fetch_era5(lat=60.39, lon=5.32, year=2021)
            df['city'] = 'Bergen'
            df['era5_year'] = 2021
        st.success("✅ Real ERA5 data loaded from Open-Meteo API")
        return df
    except Exception as e:
        st.error(f"Failed to fetch ERA5 data: {e}")
        st.info("Using fallback: empty dataset")
        return pd.DataFrame()

# Load real weather data
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

# Get available production groups from actual data
available_groups = [col for col in elhub_df.columns if col not in ['priceArea', 'month']]

if not available_groups:
    st.error("No production groups found in MongoDB data")
    st.stop()

st.subheader("Production groups")
groups = st.multiselect("Select production groups", available_groups, default=available_groups)

st.subheader("Month")
month = st.selectbox("Select month", list(range(1, 13)), index=1)

# ------------- Visuals -------------
df_area = elhub_df[elhub_df["priceArea"] == area]

# pie chart of total production
if groups:
    # Only select columns that exist in the dataframe
    valid_groups = [g for g in groups if g in df_area.columns]
    if valid_groups:
        totals = df_area[valid_groups].sum().reset_index()
        totals.columns = ["Group", "Production"]
        fig_pie = px.pie(totals, names="Group", values="Production", title=f"Total production in 2021 — {area}")
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("No valid production groups selected")
else:
    st.warning("Please select at least one production group")

# line chart of hourly production - REAL DATA from MongoDB
df_full = load_production_2021()

if df_full.empty:
    st.warning("No data available from MongoDB")
else:
    # Filter data
    if groups:
        df_line = df_full[
            (df_full['priceArea'] == area) &
            (df_full['productionGroup'].isin(groups)) &
            (df_full['startTime'].dt.month == month)
        ].copy()

        if df_line.empty:
            st.warning(f"No data found for {area}, month {month} with selected production groups")
            # Show available months for debugging
            available_months = df_full[df_full['priceArea'] == area]['startTime'].dt.month.unique()
            st.info(f"Available months for {area}: {sorted(available_months.tolist())}")
        else:
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
    else:
        st.warning("Please select at least one production group to view the line chart")

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
