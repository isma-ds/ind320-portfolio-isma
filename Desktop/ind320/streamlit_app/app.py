import streamlit as st
from pathlib import Path

st.set_page_config(page_title="IND320 Portfolio", layout="wide")

st.title("IND320 Portfolio – Home")
st.write(
    "Welcome! Use the sidebar to navigate pages. "
    "Make sure `open-meteo-subset.csv` is placed in this folder before deploying."
)

st.sidebar.title("Navigation")
st.sidebar.page_link("app.py", label="Home", icon="🏠")
st.sidebar.page_link("pages/2_Data_Table.py", label="Data Table", icon="🧮")
st.sidebar.page_link("pages/3_Plots.py", label="Plots", icon="📈")
st.sidebar.page_link("pages/4_About.py", label="About", icon="ℹ️")

st.info(
    "Tip: If the CSV is missing on Streamlit Cloud, push it to the repo under `streamlit_app/`."
)
