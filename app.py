import streamlit as st
from pathlib import Path
import pandas as pd
from lib.open_meteo import fetch_era5
from lib.mongodb_client import load_production_2021, check_mongodb_connection
from notebooks.utils_analysis import stl_production_plot, spectrogram_production_plot

st.set_page_config(
    page_title="IND320 Assignment 2 — Isma Sohail",
    page_icon="🌦️",
    layout="wide"
)

st.sidebar.title("Navigation")
st.sidebar.markdown("### 📊 IND320 — Assignment 2")
page = st.sidebar.radio("Select Page:", [
    "🏠 Home",
    "📍 Price Area Selector",
    "📈 Weather Analysis (STL + Spectrogram)",
])

# --- HOME ---
if page == "🏠 Home":
    st.title("🌦️ IND320 Assignment 2 — Weather & Energy Analysis")
    st.write("This Streamlit app integrates Open-Meteo ERA5 data with Elhub production datasets from MongoDB.")
    st.markdown("**Student:** Isma Sohail  \n**Course:** IND320 — NMBU")

    # Show MongoDB connection status
    st.subheader("📊 Database Status")
    mongo_status = check_mongodb_connection()
    if mongo_status['status'] == 'connected':
        st.success(f"✅ {mongo_status['message']}")
        st.info(f"📝 Documents in production_2021: {mongo_status['document_count']:,}")
    else:
        st.error(f"❌ {mongo_status['message']}")

# --- PRICE AREA SELECTOR ---
elif page == "📍 Price Area Selector":
    st.title("📍 Select Electricity Price Area")

    cities = pd.DataFrame({
        "priceArea": ["NO1", "NO2", "NO3", "NO4", "NO5"],
        "city": ["Oslo", "Kristiansand", "Trondheim", "Tromsø", "Bergen"],
        "lat": [59.9139, 58.1467, 63.4305, 69.6492, 60.3929],
        "lon": [10.7522, 7.9956, 10.3951, 18.9553, 5.3241]
    })

    st.dataframe(cities)
    selected_city = st.selectbox("Choose a city:", cities["city"])
    st.session_state["city"] = selected_city
    st.success(f"✅ Selected {selected_city}")

# --- WEATHER ANALYSIS ---
elif page == "📈 Weather Analysis (STL + Spectrogram)":
    st.title("📈 Weather Analysis (STL + Spectrogram)")
    city = st.session_state.get("city", "Bergen")
    st.write(f"Using {city} for 2021 (ERA5 reanalysis)")

    st.markdown("### ⛅ Fetching data from Open-Meteo API...")
    try:
        cities = {
            "Bergen": (60.3929, 5.3241),
            "Oslo": (59.9139, 10.7522),
            "Trondheim": (63.4305, 10.3951)
        }
        lat, lon = cities.get(city, (60.3929, 5.3241))
        df = fetch_era5(lat, lon, 2021)
        st.write(df.head())
    except Exception as e:
        st.error(f"Failed to fetch ERA5: {e}")

    st.markdown("### 🔹 STL Decomposition (Production)")
    # Load from MongoDB (NO CSV!)
    prod = load_production_2021()
    if prod.empty:
        st.error("Failed to load production data from MongoDB")
        st.stop()
    result = stl_production_plot(prod, area="NO5", group="Hydro")
    fig = result[0] if isinstance(result, tuple) else result
    st.plotly_chart(fig, use_container_width=True, key="stl_plot")

    st.markdown("### 🔹 Spectrogram (Production)")
    result2 = spectrogram_production_plot(prod, area="NO5", group="Hydro")
    fig2 = result2[0] if isinstance(result2, tuple) else result2
    st.plotly_chart(fig2, use_container_width=True, key="spectrogram_plot")

# --- ANOMALIES PAGE ---
elif page == "⚡ Production Anomalies (SPC + LOF)":
    st.title("⚡ Outlier & Anomaly Detection")
    st.markdown("Includes DCT-based SPC analysis for temperature and LOF-based precipitation anomaly detection.")
    st.markdown("👉 Implemented in Jupyter Notebook (`IND320_Assignment3.ipynb`) for reproducibility.")
