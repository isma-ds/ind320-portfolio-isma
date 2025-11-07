import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from lib.open_meteo import fetch_era5

st.set_page_config(page_title="PriceArea", page_icon="📍", layout="wide")

st.title("📍 Price Area Dashboard (+ Open-Meteo 2021)")
cities = pd.DataFrame([
    {"priceArea":"NO1","city":"Oslo","lat":59.9139,"lon":10.7522},
    {"priceArea":"NO2","city":"Kristiansand","lat":58.1467,"lon":7.9956},
    {"priceArea":"NO3","city":"Trondheim","lat":63.4305,"lon":10.3951},
    {"priceArea":"NO4","city":"Tromsø","lat":69.6492,"lon":18.9553},
    {"priceArea":"NO5","city":"Bergen","lat":60.3929,"lon":5.3241},
])

left, right = st.columns([1,1])

with left:
    area = st.radio("Select price area", cities["priceArea"], index=4, horizontal=True)
    st.session_state["ind320_area"] = area

    # --- Production pie (A2)
    prod = pd.read_csv("data/production_per_group_mba_hour.csv", parse_dates=["startTime"])
    pie_df = (prod[prod["priceArea"]==area]
              .groupby("productionGroup", as_index=False)["quantityKwh"].sum())
    fig = px.pie(pie_df, names="productionGroup", values="quantityKwh",
                 title=f"Total production in 2021 — {area}")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.write("**Line plot by month with group filter**")
    try:
        pills = st.pills("Production groups", sorted(prod["productionGroup"].unique()), default=["Hydro"])
        groups = pills if isinstance(pills, list) else st.multiselect(
            "Production groups", sorted(prod["productionGroup"].unique()), default=["Hydro"])
    except Exception:
        groups = st.multiselect("Production groups", sorted(prod["productionGroup"].unique()), default=["Hydro"])

    prod["month"] = prod["startTime"].dt.month
    chosen_month = st.selectbox("Month", sorted(prod["month"].unique()), index=0)
    fdf = prod[(prod["priceArea"]==area) & (prod["productionGroup"].isin(groups)) & (prod["month"]==chosen_month)]
    st.line_chart(fdf.pivot_table(index="startTime", columns="productionGroup", values="quantityKwh"), use_container_width=True)

st.divider()
with st.expander("Data source"):
    st.markdown("Production: Elhub-like CSV. Pie = totals by group; line = selected month/hourly.")

# ---- A3: Open-Meteo ERA5 download (2021) tied to selector ----
city_row = cities[cities.priceArea==area].iloc[0]
st.info(f"Downloading ERA5 for **{city_row.city} ({area})**, year **2021** …")
@st.cache_data(show_spinner=True)
def _dl(lat, lon): return fetch_era5(lat, lon, 2021)
met_df = _dl(city_row.lat, city_row.lon)
st.session_state["ind320_meteo_df"] = met_df
st.session_state["ind320_city"] = city_row.city
st.success("ERA5 cached for other pages.")
