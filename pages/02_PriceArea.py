# pages/02_PriceArea.py
# ---------------------------------
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from lib.open_meteo import get_or_fetch_era5  # our cache helper

st.set_page_config(page_title="PriceArea", page_icon="🔌", layout="wide")
st.title("⚡ Price Area Dashboard (+ Open-Meteo 2021)")

# Five price areas / cities (assignment mapping)
cities = pd.DataFrame([
    {"priceArea": "NO1", "city": "Oslo",        "lat": 59.9139, "lon": 10.7522},
    {"priceArea": "NO2", "city": "Kristiansand","lat": 58.1467, "lon": 7.9956},
    {"priceArea": "NO3", "city": "Trondheim",   "lat": 63.4305, "lon": 10.3951},
    {"priceArea": "NO4", "city": "Tromsø",      "lat": 69.6492, "lon": 18.9553},
    {"priceArea": "NO5", "city": "Bergen",      "lat": 60.3929, "lon": 5.3241},
])

left, right = st.columns([1,1])

with left:
    area = st.radio(
        "Select price area",
        cities["priceArea"], index=4, horizontal=True, key="area_radio"
    )
    row = cities[cities.priceArea == area].iloc[0]
    # Keep chosen area in session for other pages
    st.session_state["ind320_area"] = row.priceArea
    st.session_state["ind320_city"] = row.city
    st.session_state["ind320_lat"]  = float(row.lat)
    st.session_state["ind320_lon"]  = float(row.lon)

    # --- Production (A2) pie from CSV (fallback) ---
    prod = pd.read_csv("data/production_per_group_mba_hour.csv", parse_dates=["startTime"])
    pie_df = (
        prod[prod["priceArea"] == area]
        .groupby("productionGroup", as_index=False)["quantityKwh"].sum()
        .sort_values("quantityKwh", ascending=False)
    )
    fig = px.pie(pie_df, names="productionGroup", values="quantityKwh",
                 title=f"Total production in 2021 — {area}")
    st.plotly_chart(fig, use_container_width=True)

with right:
    # Production groups to include
    groups_all = list(prod["productionGroup"].unique())
    groups_sel = st.pills("Production groups", options=groups_all, selection_mode="multi",
                          default=groups_all)

    # Month selector
    month = st.selectbox("Month", list(range(1, 13)), index=0)

    mask = (
        (prod["priceArea"] == area) &
        (prod["productionGroup"].isin(groups_sel)) &
        (prod["startTime"].dt.month == month)
    )
    df_m = (
        prod.loc[mask, ["startTime", "productionGroup", "quantityKwh"]]
        .sort_values("startTime")
    )
    if df_m.empty:
        st.info("No data for this selection.")
    else:
        fig2 = px.line(
            df_m, x="startTime", y="quantityKwh", color="productionGroup",
            title=f"Hourly production — {area}, month={month}"
        )
        st.plotly_chart(fig2, use_container_width=True)

st.divider()
with st.expander("Data source"):
    st.markdown(
        "- **Production**: Elhub (assignment A2 CSV fallback loaded from `/data`).\n"
        "- **Weather**: Open-Meteo ERA5 (auto-fetched for 2021 on demand).\n"
    )

# ---- NEW: prefetch ERA5 so other pages work after cold start ----
try:
    df_met = get_or_fetch_era5(
        st, st.session_state["ind320_area"],
        st.session_state["ind320_lat"],
        st.session_state["ind320_lon"],
        year=2021
    )
    st.success(f"ERA5 cached for {st.session_state['ind320_city']} ({st.session_state['ind320_area']}).")
except Exception as e:
    st.warning(f"Could not prefetch ERA5 right now: {e}")
