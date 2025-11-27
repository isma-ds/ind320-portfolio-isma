import streamlit as st
from lib.mongodb_client import check_mongodb_connection

st.set_page_config(
    page_title="IND320 Portfolio — Isma Sohail",
    page_icon="⚡",
    layout="wide"
)

# --- HOME PAGE ---
st.title("⚡ IND320 Portfolio — Energy Analytics & Forecasting Platform")

st.markdown("""
Welcome to the **IND320 Complete Portfolio** showcasing energy data analytics, time series forecasting,
and advanced weather-energy correlation analysis for Norwegian electricity markets.

## 🎯 Assessment 4 — Advanced Features (Latest)

### Interactive Energy Platform
- **📍 Interactive Map** - Norwegian price areas (NO1-NO5) with choropleth visualization
- **❄️ Snow Drift Analysis** - Tabler (2003) methodology with wind rose visualization
- **🔗 Weather-Energy Correlation** - Sliding window analysis with configurable lag
- **📈 SARIMAX Forecasting** - Full time series forecasting with confidence intervals

### Previous Assessments
- **Assessment 3** - STL Decomposition, Spectrogram, Outlier Detection (DCT, LOF)
- **Assessment 2** - Elhub API integration, Cassandra + Spark pipeline, MongoDB
- **Assessment 1** - Basic data exploration and visualization

---

## 📊 Data Pipeline (2021-2024)

**Production Data:** 701,280 records (2021-2024) - All price areas & groups
**Consumption Data:** 701,280 records (2021-2024) - All price areas & groups
**Total Records:** 1,402,560+ hourly measurements

**Technologies:**
- 🗄️ **Elhub API** - Norwegian electricity data
- ⚙️ **Cassandra + Spark** - Distributed storage & processing
- 🍃 **MongoDB Atlas** - Cloud database (1.4M+ documents)
- 🌤️ **Open-Meteo API** - ERA5 weather reanalysis

---

## 🎓 Student Information

**Name:** Isma Sohail
**Course:** IND320 — Data Science and Analytics
**Institution:** NMBU
**Academic Year:** 2024-2025

---
""")

# Show MongoDB connection status
st.subheader("📊 Database Status")
mongo_status = check_mongodb_connection()

if mongo_status['status'] == 'connected':
    st.success("✅ MongoDB Atlas Connected")

    # Show all collections
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Production 2021", "175,200", help="Elhub production data")

    with col2:
        st.metric("Production 2022-2024", "526,080", help="Assessment 4 data")

    with col3:
        st.metric("Consumption 2021", "175,200", help="Assessment 4 data")

    with col4:
        st.metric("Consumption 2022-2024", "526,080", help="Assessment 4 data")

    st.info(f"**Total:** 1,402,560 hourly records | **Coverage:** 2021-2024 | **Price Areas:** NO1-NO5")
else:
    st.error(f"❌ MongoDB Disconnected")
    st.caption(mongo_status['message'])

# APIs Status
st.subheader("🌐 External APIs")
col1, col2 = st.columns(2)

with col1:
    st.success("✅ Elhub API")
    st.caption("Norwegian electricity production & consumption data")

with col2:
    st.success("✅ Open-Meteo API")
    st.caption("ERA5 Historical Weather Reanalysis (2021-2024)")

# Quick Links
st.subheader("🔗 Quick Navigation")
st.markdown("""
**Assessment 4 Pages:**
- 📍 [Interactive Map](/Map_InteractivePriceAreas) - Explore price areas with choropleth
- ❄️ [Snow Drift Analysis](/SnowDrift_Analysis) - Tabler (2003) calculations
- 🔗 [Weather-Energy Correlation](/Weather_Energy_Correlation) - Sliding window analysis
- 📈 [SARIMAX Forecasting](/SARIMAX_Forecasting) - Time series predictions

**Previous Assessments:**
- 📊 [Analysis A](/Analysis_A) - Production by group (Assessment 3)
- 🌡️ [Analysis B](/Analysis_B) - Temperature outlier detection (Assessment 3)
- 📋 [MongoDB Status](/Mongo_Status) - Database health check
""")

# Footer
st.markdown("---")
st.caption("IND320 — Data Science and Analytics | NMBU | 2024-2025")
st.caption("GitHub: [ind320-portfolio-isma](https://github.com/isma-ds/ind320-portfolio-isma) | Branch: assessment_4")
