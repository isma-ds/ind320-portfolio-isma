import streamlit as st
from lib.mongodb_client import check_mongodb_connection

st.set_page_config(
    page_title="IND320 Assignment 3 — Isma Sohail",
    page_icon="🌦️",
    layout="wide"
)

# --- HOME PAGE ---
st.title("🌦️ IND320 Assignment 3 — Advanced Weather & Energy Analysis")

st.markdown("""
Welcome to the IND320 Assignment 3 Streamlit app! This application demonstrates advanced 
time series analysis techniques including:

- **STL Decomposition** - Seasonal-Trend decomposition using LOESS
- **Spectrogram Analysis** - Frequency-time domain visualization
- **Temperature Outlier Detection** - Using DCT + Statistical Process Control
- **Precipitation Anomaly Detection** - Using Local Outlier Factor

### 📊 Data Sources
- **Elhub Production Data** (2021) - From MongoDB Atlas
- **Open-Meteo Weather Data** (ERA5 Historical Reanalysis)

### 🎓 Student Information
**Name:** Isma Sohail  
**Course:** IND320 — NMBU  
**Assignment:** Part 3 of 4

---
""")

# Show MongoDB connection status
st.subheader("📊 Database Status")
mongo_status = check_mongodb_connection()

col1, col2 = st.columns(2)

with col1:
    if mongo_status['status'] == 'connected':
        st.success(f"✅ MongoDB Connected")
        st.metric("Documents in production_2021", f"{mongo_status['document_count']:,}")
    else:
        st.error(f"❌ MongoDB Disconnected")
        st.caption(mongo_status['message'])

with col2:
    st.info("📡 Open-Meteo API")
    st.caption("ERA5 Historical Reanalysis (2021)")


# Footer
st.markdown("---")
st.caption("IND320 — Data Science and Analytics | NMBU | 2024-2025")
