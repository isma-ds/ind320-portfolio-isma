# pages/02_PriceArea.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
from datetime import timezone

st.set_page_config(page_title="PriceArea", page_icon="⚡", layout="wide")
st.title("⚡ Price Area Dashboard (Elhub demo + Open-Meteo 2021)")

DATA_PATH = Path("data/production_per_group_mba_hour.csv")
AREAS = ["NO1", "NO2", "NO3", "NO4", "NO5"]
GROUPS = ["Hydro", "Wind", "Thermal"]

CITIES = pd.DataFrame([
    {"priceArea":"NO1","city":"Oslo",        "lat":59.9139, "lon":10.7522},
    {"priceArea":"NO2","city":"Kristiansand","lat":58.1467, "lon":7.9956},
    {"priceArea":"NO3","city":"Trondheim",  "lat":63.4305, "lon":10.3951},
    {"priceArea":"NO4","city":"Tromsø",     "lat":69.6492, "lon":18.9553},
    {"priceArea":"NO5","city":"Bergen",     "lat":60.3929, "lon":5.3241},
])

def _is_complete(df: pd.DataFrame) -> bool:
    try:
        if not {"priceArea","productionGroup","startTime","quantitykWh"}.issubset(df.columns):
            return False
        combos = set(zip(df["priceArea"], df["productionGroup"]))
        needed = {(a,g) for a in AREAS for g in GROUPS}
        if not needed.issubset(combos):
            return False
        df2 = df.copy()
        df2["startTime"] = pd.to_datetime(df2["startTime"], utc=True)
        total = len(df2)
        return (df2["startTime"].min().year == 2021
                and df2["startTime"].max().year == 2021
                and total >= 5*3*8000)
    except Exception:
        return False

def _synthesize_production() -> pd.DataFrame:
    idx = pd.date_range("2021-01-01", "2021-12-31 23:00", freq="H", tz=timezone.utc)
    rows = []
    rng = np.random.default_rng(42)
    base_by_group = {"Hydro": 4800, "Wind": 2600, "Thermal": 900}
    area_factor = {"NO1":1.00, "NO2":0.95, "NO3":0.85, "NO4":0.75, "NO5":1.05}

    for area in AREAS:
        for group in GROUPS:
            base = base_by_group[group] * area_factor[area]
            t = np.arange(len(idx))
            daily = 1.0 + 0.06*np.sin(2*np.pi*(t % 24)/24.0)
            weekly = 1.0 + 0.08*np.sin(2*np.pi*(t % (24*7))/(24*7))
            annual = 1.0 + 0.10*np.sin(2*np.pi*t/(24*365))
            noise = rng.normal(0, 60, size=len(idx))
            q = base * daily * weekly * annual + noise
            q = np.clip(q, 150, None).astype(int)

            rows.append(pd.DataFrame({
                "priceArea": area,
                "productionGroup": group,
                "startTime": idx,
                "quantitykWh": q
            }))
    return pd.concat(rows, ignore_index=True)

# Load or build complete dataset
if DATA_PATH.exists():
    prod = pd.read_csv(DATA_PATH)
    if not _is_complete(prod):
        prod = _synthesize_production()
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        prod.to_csv(DATA_PATH, index=False)
else:
    prod = _synthesize_production()
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    prod.to_csv(DATA_PATH, index=False)

# Clean
prod["startTime"] = pd.to_datetime(prod["startTime"], utc=True)
prod["month"] = prod["startTime"].dt.month
prod = prod.sort_values(["priceArea","productionGroup","startTime"]).reset_index(drop=True)

# Selectors
st.markdown("Select price area")
area = st.radio("Select price area", AREAS, index=AREAS.index("NO5"),
                horizontal=True, label_visibility="collapsed")

# ⬇️ Changed from st.pills(...) to st.multiselect(...) for Streamlit Cloud compatibility
grp_sel = st.multiselect("Production groups", GROUPS, default=GROUPS, key="grp_sel")

month = st.selectbox("Month", list(range(1,13)), index=1)

# Share selection to other pages
row = CITIES[CITIES["priceArea"] == area].iloc[0].to_dict()
st.session_state["ind320_area"] = area
st.session_state["ind320_city_row"] = row

# Layout
left, right = st.columns([1.0, 1.4])

with left:
    year_df = prod[(prod["priceArea"] == area)]
    pie_df = year_df.groupby("productionGroup", as_index=False)["quantitykWh"].sum()
    fig_pie = px.pie(pie_df, names="productionGroup", values="quantitykWh",
                     title=f"Total production in 2021 — {area}", hole=0.0)
    fig_pie.update_layout(
        legend_title="productionGroup",
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="white")
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with right:
    month_df = prod[
        (prod["priceArea"] == area) &
        (prod["productionGroup"].isin(grp_sel)) &
        (prod["month"] == month)
    ]
    if month_df.empty:
        st.warning("No data for this combination.")
    else:
        fig_line = px.line(
            month_df, x="startTime", y="quantitykWh",
            color="productionGroup",
            title=f"Hourly production — {area}, month={month}"
        )
        fig_line.update_layout(
            xaxis_title="startTime", yaxis_title="quantitykWh",
            plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
            font=dict(color="white"), legend_title="productionGroup"
        )
        st.plotly_chart(fig_line, use_container_width=True)

with st.expander("Data source"):
    st.write(f"""
This page uses `{DATA_PATH}`. If it was missing or incomplete, a full **demo** for
**NO1–NO5 × Hydro/Wind/Thermal** (8760 hours per combo, year 2021) was generated.
Replace the CSV with your own Elhub export (same columns) to use real data.
""")
