# pages/03_Analysis_A.py
import streamlit as st
import pandas as pd
from notebooks.utils_analysis import (
    stl_production_plot, spectrogram_production_plot, combos_available
)

st.set_page_config(page_title="Analysis A — STL & Spectrogram", page_icon="⚡", layout="wide")
st.title("⚡ Analysis A — STL & Spectrogram (Elhub production)")

# -------- data (CSV fallback) --------
@st.cache_data
def load_prod():
    path = "data/production_per_group_mba_hour.csv"
    df = pd.read_csv(path, parse_dates=["startTime"])
    return df

prod = load_prod()
avail_map, avail_table = combos_available(prod)

# -------- UI --------
st.subheader("Price area")
areas = ["NO1", "NO2", "NO3", "NO4", "NO5"]
area = st.radio("", areas, index=areas.index("NO5"), horizontal=True)

valid_groups = avail_map.get(area, [])
if not valid_groups:
    st.warning(f"No production groups available for {area} in your CSV.")
    st.dataframe(avail_table, use_container_width=True)
    st.stop()

st.subheader("Production group")
group = st.selectbox("", valid_groups, index=0, key="a3_group")

tabs = st.tabs(["STL decomposition", "Spectrogram"])

with tabs[0]:
    c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 0.8])
    with c1:
        period = st.number_input("STL period (hours)", value=24*7, min_value=24, step=24)
    with c2:
        seasonal = st.slider("Seasonal smoother", 7, 61, 13, step=2)
    with c3:
        trend = st.slider("Trend smoother", 7, 121, 31, step=2)
    with c4:
        robust = st.checkbox("Robust", value=True)

    fig, ok, msg = stl_production_plot(
        prod, area=area, group=group,
        period=period, seasonal=seasonal, trend=trend, robust=robust
    )
    if ok:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(msg)
        st.dataframe(avail_table, use_container_width=True)

with tabs[1]:
    c1, c2, c3 = st.columns([1.2, 1.2, 0.8])
    with c1:
        window_len = st.number_input("Window length (hours)", value=24*7, min_value=32, step=24)
    with c2:
        overlap = st.slider("Window overlap", 0.0, 0.9, 0.5, step=0.05)
    with c3:
        polar = st.checkbox("Polar view (circle)", value=False)

    fig, ok, msg = spectrogram_production_plot(
        prod, area=area, group=group,
        window_len=int(window_len), overlap=float(overlap), polar=polar
    )
    if ok:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(msg)
        st.dataframe(avail_table, use_container_width=True)
