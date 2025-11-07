# pages/03_Analysis_A.py
import streamlit as st
import pandas as pd
from notebooks.utils_analysis import (
    load_production_csv,
    stl_production_plot,
    spectrogram_production_plot,
)

st.set_page_config(page_title="Analysis A — STL & Spectrogram", layout="wide")

st.title("⚡ Analysis A — STL & Spectrogram (Elhub production)")

# --- Shared controls (area + group) ---
with st.container():
    st.subheader("Price area")
    col_area = st.columns(5)
    areas = ["NO1", "NO2", "NO3", "NO4", "NO5"]
    # Default to session state from PriceArea (if any), else NO5
    default_area = st.session_state.get("ind320_area", "NO5")
    area_index = areas.index(default_area) if default_area in areas else 4
    area = st.radio(" ", areas, index=area_index, horizontal=True, label_visibility="collapsed")

grp = st.selectbox("Production group", ["Hydro", "Wind", "Thermal"], index=0)

# --- Load CSV robustly (local packaged CSV from A2 fallback) ---
@st.cache_data(show_spinner=False)
def _load_prod():
    return load_production_csv("data/production_per_group_mba_hour.csv")

try:
    prod = _load_prod()
except Exception as e:
    st.error(f"Could not load production CSV: {e}")
    st.stop()

# --- Tabs ---
tab1, tab2 = st.tabs(["STL decomposition", "Spectrogram"])

with tab1:
    c1, c2, c3, c4 = st.columns([1,1,1,1])
    period = c1.number_input("STL period (hours)", min_value=4, max_value=24*60, step=4, value=24*7)
    seasonal = c2.slider("Seasonal smoother", 7, 61, 13, step=2)
    trend = c3.slider("Trend smoother", 7, 121, 31, step=2)
    robust = c4.checkbox("Robust", value=True)

    try:
        fig = stl_production_plot(
            prod, area=area, group=grp,
            period_hours=int(period), seasonal=int(seasonal), trend=int(trend),
            robust=bool(robust),
            title="STL Decomposition — Production"
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(str(e))

with tab2:
    c1, c2 = st.columns(2)
    win = c1.slider("Window length (hours)", 24, 24*28, 24*7, step=24)
    ov  = c2.slider("Window overlap", 0.0, 0.9, 0.5, step=0.1)
    try:
        fig2 = spectrogram_production_plot(
            prod, area=area, group=grp, window_len=int(win), overlap=float(ov)
        )
        st.plotly_chart(fig2, use_container_width=True)
    except Exception as e:
        st.error(str(e))
