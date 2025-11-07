import streamlit as st
import pandas as pd
from notebooks.utils_analysis import stl_production_plot, spectrogram_production_plot

st.set_page_config(page_title="Analysis A", page_icon="📈", layout="wide")
st.title("📈 Analysis A — STL & Spectrogram")

area = st.session_state.get("ind320_area", "NO5")
prod = pd.read_csv("data/production_per_group_mba_hour.csv", parse_dates=["startTime"])
groups = sorted(prod["productionGroup"].unique())

tab1, tab2 = st.tabs(["STL decomposition", "Spectrogram"])

with tab1:
    g = st.selectbox("Production group", groups, index=0)
    period = st.number_input("STL period (hours)", min_value=24, max_value=24*21, value=24*7, step=24)
    seasonal = st.slider("Seasonal smoother", 7, 61, 13, step=2)
    trend = st.slider("Trend smoother", 7, 121, 31, step=2)
    robust = st.checkbox("Robust", True)
    fig = stl_production_plot(prod, area=area, group=g, period=period, seasonal=seasonal, trend=trend, robust=robust)
    st.pyplot(fig, use_container_width=True)

with tab2:
    g2 = st.selectbox("Production group (spectrogram)", groups, index=0, key="specg")
    window = st.slider("Window length (hours)", 24*3, 24*28, 24*7, step=24)
    overlap = st.slider("Window overlap", 0.0, 0.9, 0.5, step=0.1)
    fig2 = spectrogram_production_plot(prod, area=area, group=g2, window_len=window, overlap=overlap)
    st.pyplot(fig2, use_container_width=True)
