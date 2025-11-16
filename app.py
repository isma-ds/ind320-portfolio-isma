"""
IND320 Assessment 4 - Interactive Energy Analytics Platform
Main entry point for the Streamlit application

Student: Isma Sohail
Course: IND320 - NMBU
"""

import streamlit as st

st.set_page_config(
    page_title="IND320 Assessment 4 - Energy Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main page content
st.title("⚡ IND320 Assessment 4 - Interactive Energy Analytics Platform")

st.markdown("""
Welcome to the comprehensive energy analytics platform for Norwegian electricity markets.
This application combines energy data, meteorological analysis, and advanced forecasting tools.

**Student:** Isma Sohail
**Course:** IND320 - NMBU
**Assessment:** 4 (Final Portfolio Project)
""")

# Overview section
st.header("📋 Platform Overview")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🗺️ Data & Visualization")
    st.markdown("""
    - **Interactive Map**: Select locations and view Norwegian price areas
    - **Energy Choropleth**: Visualize production/consumption patterns
    - **1.4M+ Records**: Hourly energy data for 2021-2024
    - **5 Price Areas**: NO1-NO5 coverage
    """)

with col2:
    st.subheader("🔬 Analysis Tools")
    st.markdown("""
    - **Snow Drift Analysis**: Meteorological calculations
    - **Correlation Analysis**: Weather-energy relationships
    - **SARIMAX Forecasting**: Advanced time series predictions
    - **Real-time Data**: Open-Meteo API integration
    """)


# Features showcase
st.header("🚀 Key Features")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ Interactive Map",
    "🌡️ Energy Choropleth",
    "❄️ Snow Drift",
    "📊 Correlation",
    "🔮 Forecasting"
])

with tab1:
    st.markdown("""
    ### Interactive Map with Norwegian Price Areas

    **Features:**
    - GeoJSON visualization of 5 Norwegian electricity price areas
    - Click or manually enter coordinates
    - Price area selection and highlighting
    - Quick presets for major cities (Oslo, Bergen, Trondheim)

    **Use Case:**
    Select a location for snow drift analysis and meteorological data fetching.

    **Navigation:** See sidebar → Interactive Map
    """)

with tab2:
    st.markdown("""
    ### Energy Production/Consumption Choropleth

    **Features:**
    - Color-coded visualization of energy metrics by price area
    - Production groups: Hydro, Wind, Thermal, Solar
    - Consumption groups: Residential, Commercial, Industrial, Other
    - Time period selection
    - Time series comparisons

    **Use Case:**
    Identify regions with high/low production or consumption patterns.

    **Navigation:** See sidebar → Energy Choropleth
    """)

with tab3:
    st.markdown("""
    ### Snow Drift Analysis

    **Features:**
    - Meteorological physics-based snow drift calculations
    - Wind rose diagrams showing prevailing wind directions
    - Yearly, monthly, and daily snow drift patterns
    - Water year definition (July-June)

    **Use Case:**
    Understand snow accumulation patterns important for hydroelectric power planning.

    **Navigation:** See sidebar → Snow Drift
    """)

with tab4:
    st.markdown("""
    ### Meteorology-Energy Correlation

    **Features:**
    - Sliding window correlation analysis
    - Adjustable lag parameters (weather leads/lags energy)
    - Window size selection (7-90 days)
    - Multiple weather variables: temperature, precipitation, wind

    **Use Case:**
    Discover relationships between weather patterns and energy demand/production.

    **Navigation:** See sidebar → Correlation Analysis
    """)

with tab5:
    st.markdown("""
    ### SARIMAX Forecasting

    **Features:**
    - Full SARIMAX parameter control (p,d,q,P,D,Q,s)
    - Training data period selection
    - Forecast horizon up to 90 days
    - Exogenous variables (weather data)
    - 95% confidence intervals
    - Model diagnostics (AIC, BIC)

    **Use Case:**
    Predict future energy production or consumption based on historical patterns and weather.

    **Navigation:** See sidebar → SARIMAX Forecasting
    """)


# Data information
st.header("💾 Data Sources")

st.markdown("""
### Energy Data
- **Source:** Synthetic data generated to match Elhub API structure
- **Coverage:** 2021-2024 (hourly resolution)
- **Records:** 1,402,560 total
- **Storage:** MongoDB Atlas (4 collections)
- **Areas:** NO1, NO2, NO3, NO4, NO5
- **Groups:** Production (Hydro, Wind, Thermal, Solar) + Consumption (Residential, Commercial, Industrial, Other)

### Meteorological Data
- **Source:** Open-Meteo ERA5 Reanalysis
- **API:** https://open-meteo.com
- **Variables:** Temperature, precipitation, wind speed, sunshine duration
- **Resolution:** Hourly and daily aggregations

### Geographic Data
- **Source:** NVE (Norwegian Water Resources and Energy Directorate)
- **Format:** GeoJSON with polygon boundaries
- **Coordinate System:** EUREF 89 / ETRS 89
""")


# Technical details
with st.expander("🔧 Technical Details"):
    st.markdown("""
    ### Technology Stack

    **Frontend:**
    - Streamlit (interactive web application)
    - Plotly (interactive visualizations)
    - Pandas (data manipulation)

    **Backend:**
    - MongoDB Atlas (cloud database)
    - Open-Meteo API (weather data)
    - Python 3.12

    **Analytics:**
    - Statsmodels (SARIMAX forecasting)
    - SciPy (correlation analysis)
    - NumPy (numerical computations)

    ### Performance Optimizations

    - **Caching:** @st.cache_data for expensive operations
    - **Indexing:** MongoDB indexes on startTime and priceArea
    - **Lazy Loading:** Data fetched only when needed
    - **Batch Processing:** MongoDB queries optimized for large datasets

    ### Error Handling

    - Graceful handling of missing data
    - User-friendly error messages
    - Fallback to default values where appropriate
    - Connection retry logic for API calls
    """)


# Usage instructions
st.header("📖 How to Use This Platform")

st.markdown("""
### Quick Start Guide

1. **Select a Location**
   - Navigate to "Interactive Map" in the sidebar
   - Click on the map or enter coordinates manually
   - Your selection will be used for snow drift and correlation analysis

2. **Explore Energy Data**
   - Visit "Energy Choropleth" to see production/consumption patterns
   - Select different price areas, time periods, and energy groups
   - Compare areas using the time series plot

3. **Analyze Snow Drift**
   - Go to "Snow Drift" page
   - Select a year range
   - View yearly, monthly, and daily snow accumulation
   - Examine wind rose diagrams

4. **Study Correlations**
   - Open "Correlation Analysis"
   - Choose weather variable and energy metric
   - Adjust window size and lag parameters
   - Interpret correlation changes over time

5. **Generate Forecasts**
   - Navigate to "SARIMAX Forecasting"
   - Select energy metric and training period
   - Configure SARIMAX parameters
   - Click "Train Model" to generate predictions
   - View forecast with confidence intervals

### Tips for Best Results

- **Snow Drift:** Use locations in mountainous areas for more dramatic patterns
- **Correlation:** Try different lag values to find leading/lagging relationships
- **Forecasting:** Start with simple parameters (low p,d,q values) and increase as needed
- **Comparison:** Use same time periods across different analyses for consistency
""")


# Project links
st.header("🔗 Project Links")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **GitHub Repository**

    [github.com/isma-ds/ind320-portfolio-isma](https://github.com/isma-ds/ind320-portfolio-isma)

    Branch: `assessment4`
    """)

with col2:
    st.markdown("""
    **Streamlit App**

    [Deployment URL will be here]

    Status: Development
    """)

with col3:
    st.markdown("""
    **Documentation**

    - Jupyter Notebook
    - Requirements Analysis
    - Implementation Guide
    """)


# Footer
st.markdown("---")
st.caption("""
Assessment 4 - IND320 Energy Analytics Platform | Student: Isma Sohail | NMBU 2025
Data: Synthetic Elhub-style + Open-Meteo ERA5 | Technology: Python, Streamlit, MongoDB, Plotly
""")

# Sidebar information
with st.sidebar:
    st.markdown("---")
    st.markdown("### 💡 Quick Links")
    st.markdown("""
    - [GitHub Repo](https://github.com/isma-ds/ind320-portfolio-isma)
    - [Documentation](./notebooks/IND320_Assignment4.ipynb)
    """)

    st.markdown("---")
    st.markdown("### 📊 Data Status")

    try:
        from pymongo import MongoClient

        mongo_uri = st.secrets.get("MONGO_URI", "mongodb+srv://ismasohail_user:IsmaMinhas@cluster0.e3wct64.mongodb.net/ind320?retryWrites=true&w=majority&appName=Cluster0")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
        client.admin.command('ping')

        st.success("MongoDB: Connected")

        db = client["ind320"]
        collections = ["elhub_production_2021", "elhub_consumption_2021",
                      "elhub_production_2022_2024", "elhub_consumption_2022_2024"]

        total_records = sum([db[coll].count_documents({}) for coll in collections])
        st.info(f"Total Records: {total_records:,}")

        client.close()

    except:
        st.warning("MongoDB: Not Connected")
        st.info("Using fallback data sources")
