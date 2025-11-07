import streamlit as st
import pandas as pd
from pathlib import Path

# Robust import: works both locally and on Streamlit Cloud
try:
    from notebooks.utils_analysis import stl_production_plot, spectrogram_production_plot
except ModuleNotFoundError:
    from utils_analysis import stl_production_plot, spectrogram_production_plot

st.set_page_config(page_title="Analysis A — STL & Spectrogram", layout="wide")

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "production_per_group_mba_hour.csv"

@st.cache_data
def load_prod(path: Path):
    df = pd.read_csv(path)
    # Expected columns: priceArea, productionGroup, startTime, quantitykWh
    df["startTime"] = pd.to_datetime(df["startTime"], utc=True, errors="coerce")
    return df.dropna(subset=["startTime"])

df = load_prod(DATA_PATH)

st.title("⚡ Analysis A — STL & Spectrogram (Elhub production)")

# Use global selector from page 02 if available, else default NO5
area_default = st.session_state.get("ind320_area", "NO5")
AREAS = ["NO1", "NO2", "NO3", "NO4", "NO5"]
area = st.radio("Price area", AREAS, index=AREAS.index(area_default), horizontal=True)

groups = sorted(df["productionGroup"].unique().tolist())
group = st.selectbox("Production group", groups, index=0)

tab_stl, tab_spec = st.tabs(["STL decomposition", "Spectrogram"])

with tab_stl:
    cols = st.columns([1,1,1,1,1])
    period = cols[0].number_input("STL period (hours)", min_value=24, max_value=24*60, value=24*7, step=24)
    seasonal = cols[1].slider("Seasonal smoother", 7, 121, 13, 2)
    trend = cols[2].slider("Trend smoother", 7, 121, 31, 2)
    robust = cols[3].checkbox("Robust", True)
    cols[4].markdown("")  # spacer

    fig = stl_production_plot(
        df,
        area=area,
        group=group,
        period=int(period),
        seasonal=int(seasonal),
        trend=int(trend),
        robust=bool(robust),
    )
    st.plotly_chart(fig, use_container_width=True)

with tab_spec:
    cols = st.columns([1,1,1])
    window_len = cols[0].number_input("Window length (hours)", min_value=24, max_value=24*30, value=24*7, step=24)
    overlap = cols[1].slider("Window overlap", 0.0, 0.9, 0.5, 0.05)

    fig2 = spectrogram_production_plot(
        df,
        area=area,
        group=group,
        window_len=int(window_len),
        overlap=float(overlap),
    )
    st.plotly_chart(fig2, use_container_width=True)
