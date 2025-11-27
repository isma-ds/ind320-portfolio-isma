# pages/10_Weather_Energy_Correlation.py
"""
Meteorology and Energy Production/Consumption Correlation Analysis
Assessment 4 - New Feature

Sliding window correlation with selectable lag and window length.
Analyzes relationships between weather conditions and energy patterns.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import sys
sys.path.append('..')
from lib.mongodb_client import load_production_all_years, load_consumption_all_years

st.set_page_config(page_title="Weather-Energy Correlation", page_icon="🌤️", layout="wide")

# ============================================================================
# TITLE AND DESCRIPTION
# ============================================================================

st.title("🌤️ Weather-Energy Correlation Analysis")
st.markdown("""
This page analyzes the correlation between meteorological properties and energy production/consumption
using a sliding window approach with configurable lag and window length.
""")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

@st.cache_data(ttl=3600)
def fetch_weather_for_area(latitude, longitude, start_date, end_date):
    """Fetch hourly weather data from Open-Meteo"""
    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "hourly": ["temperature_2m", "precipitation", "wind_speed_10m", "wind_direction_10m",
                   "relative_humidity_2m", "surface_pressure"],
        "timezone": "UTC"
    }

    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()

        df = pd.DataFrame({
            'time': pd.to_datetime(data['hourly']['time']),
            'temperature': data['hourly']['temperature_2m'],
            'precipitation': data['hourly']['precipitation'],
            'wind_speed': data['hourly']['wind_speed_10m'],
            'wind_direction': data['hourly']['wind_direction_10m'],
            'humidity': data['hourly']['relative_humidity_2m'],
            'pressure': data['hourly']['surface_pressure']
        })

        return df

    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return None

def compute_sliding_correlation(series1, series2, window_size, lag=0):
    """
    Compute sliding window correlation between two time series.

    Args:
        series1: First time series (weather)
        series2: Second time series (energy)
        window_size: Size of sliding window
        lag: Lag to apply to series2 (positive = series2 lags series1)

    Returns:
        DataFrame with time index and correlation values
    """
    if lag > 0:
        series2 = series2.shift(lag)
    elif lag < 0:
        series1 = series1.shift(-lag)

    # Align series
    df = pd.DataFrame({'s1': series1, 's2': series2}).dropna()

    if len(df) < window_size:
        return pd.DataFrame()

    # Compute rolling correlation
    correlation = df['s1'].rolling(window=window_size).corr(df['s2'])

    result = pd.DataFrame({
        'time': df.index,
        'correlation': correlation
    })

    return result.dropna()

# ============================================================================
# PRICE AREA COORDINATES (Approximate centers)
# ============================================================================

AREA_COORDS = {
    'NO1': (60.0, 11.0),  # Oslo region
    'NO2': (58.5, 7.5),   # Kristiansand region
    'NO3': (63.5, 10.5),  # Trondheim region
    'NO4': (69.5, 19.0),  # Tromsø region
    'NO5': (60.5, 6.0)    # Bergen region
}

# ============================================================================
# SIDEBAR CONTROLS
# ============================================================================

st.sidebar.header("Analysis Parameters")

# Price area selector
price_area = st.sidebar.selectbox(
    "Price Area",
    options=list(AREA_COORDS.keys()),
    help="Select the price area for analysis"
)

lat, lon = AREA_COORDS[price_area]
st.sidebar.info(f"📍 Coordinates: {lat}°N, {lon}°E")

# Data type selector
data_type = st.sidebar.radio(
    "Energy Data Type",
    options=["Production", "Consumption"],
    help="Select production or consumption data"
)

# Group selector
if data_type == "Production":
    energy_groups = ['Wind', 'Hydro', 'Thermal', 'Solar']
else:
    energy_groups = ['Total']  # Simplified for consumption

energy_group = st.sidebar.selectbox(
    f"{data_type} Group",
    options=energy_groups
)

# Weather property selector
weather_property = st.sidebar.selectbox(
    "Weather Property",
    options=['temperature', 'wind_speed', 'precipitation', 'humidity', 'pressure'],
    help="Select the meteorological property to correlate"
)

# Time range
st.sidebar.subheader("Time Range")

col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "Start Date",
        value=datetime(2021, 1, 1),
        min_value=datetime(2021, 1, 1),
        max_value=datetime(2024, 11, 30)
    )

with col2:
    end_date = st.date_input(
        "End Date",
        value=datetime(2021, 12, 31),
        min_value=datetime(2021, 1, 1),
        max_value=datetime(2024, 11, 30)
    )

if start_date >= end_date:
    st.sidebar.error("End date must be after start date")
    st.stop()

# Window and lag parameters
st.sidebar.subheader("Correlation Parameters")

window_hours = st.sidebar.slider(
    "Window Size (hours)",
    min_value=24,
    max_value=24*30,  # 30 days
    value=24*7,  # 1 week
    step=24,
    help="Size of the sliding window for correlation calculation"
)

lag_hours = st.sidebar.slider(
    "Lag (hours)",
    min_value=-72,
    max_value=72,
    value=0,
    step=1,
    help="Positive lag: energy lags weather. Negative lag: weather lags energy"
)

# ============================================================================
# LOAD DATA
# ============================================================================

st.subheader("Loading Data...")

progress_bar = st.progress(0)
status_text = st.empty()

# Load energy data
status_text.text("Loading energy data from MongoDB...")
progress_bar.progress(25)

if data_type == "Production":
    energy_df = load_production_all_years()
    group_col = 'productionGroup'
else:
    energy_df = load_consumption_all_years()
    group_col = 'consumptionGroup'

if energy_df.empty:
    st.error(f"No {data_type.lower()} data available")
    st.stop()

# Filter by price area and group
energy_df = energy_df[energy_df['priceArea'] == price_area]

if data_type == "Production" and energy_group != "All":
    energy_df = energy_df[energy_df[group_col] == energy_group]

# Filter by date range
energy_df = energy_df[
    (energy_df['startTime'] >= pd.Timestamp(start_date)) &
    (energy_df['startTime'] <= pd.Timestamp(end_date))
]

if energy_df.empty:
    st.error(f"No data available for {price_area} - {energy_group} in selected date range")
    st.stop()

# Aggregate to hourly if needed
qty_col = 'quantityKwh' if 'quantityKwh' in energy_df.columns else 'quantityMWh'
energy_hourly = energy_df.groupby('startTime')[qty_col].sum().reset_index()
energy_hourly.columns = ['time', 'quantity']
energy_hourly = energy_hourly.set_index('time').sort_index()

progress_bar.progress(50)

# Load weather data
status_text.text("Fetching weather data from Open-Meteo...")

weather_df = fetch_weather_for_area(lat, lon, start_date, end_date)

if weather_df is None or weather_df.empty:
    st.error("Failed to fetch weather data")
    st.stop()

weather_df = weather_df.set_index('time').sort_index()

progress_bar.progress(75)

# Align time series
status_text.text("Aligning and computing correlations...")

# Merge on common timestamps
merged_df = pd.merge(
    energy_hourly,
    weather_df[[weather_property]],
    left_index=True,
    right_index=True,
    how='inner'
)

if merged_df.empty:
    st.error("No overlapping timestamps between energy and weather data")
    st.stop()

progress_bar.progress(90)

# Compute sliding correlation
correlation_df = compute_sliding_correlation(
    merged_df[weather_property],
    merged_df['quantity'],
    window_size=window_hours,
    lag=lag_hours
)

progress_bar.progress(100)
status_text.text("✅ Data loaded and correlations computed!")

st.success(f"Analyzing {len(merged_df):,} hours of data from {start_date} to {end_date}")

# ============================================================================
# VISUALIZATIONS
# ============================================================================

# Create subplot figure
fig = make_subplots(
    rows=3,
    cols=1,
    subplot_titles=(
        f"{weather_property.replace('_', ' ').title()}",
        f"{data_type} - {energy_group}",
        f"Sliding Window Correlation (window={window_hours}h, lag={lag_hours}h)"
    ),
    vertical_spacing=0.1,
    row_heights=[0.25, 0.25, 0.5]
)

# Plot 1: Weather data
fig.add_trace(
    go.Scatter(
        x=merged_df.index,
        y=merged_df[weather_property],
        mode='lines',
        name=weather_property.title(),
        line=dict(color='blue', width=1)
    ),
    row=1, col=1
)

# Plot 2: Energy data
fig.add_trace(
    go.Scatter(
        x=merged_df.index,
        y=merged_df['quantity'],
        mode='lines',
        name=f"{data_type}",
        line=dict(color='green', width=1)
    ),
    row=2, col=1
)

# Plot 3: Correlation
fig.add_trace(
    go.Scatter(
        x=correlation_df['time'],
        y=correlation_df['correlation'],
        mode='lines',
        name='Correlation',
        line=dict(color='red', width=2),
        fill='tozeroy'
    ),
    row=3, col=1
)

# Add zero line for correlation
fig.add_hline(y=0, line_dash="dash", line_color="gray", row=3, col=1)

# Update axes
fig.update_xaxes(title_text="Time", row=3, col=1)
fig.update_yaxes(title_text=weather_property.replace('_', ' ').title(), row=1, col=1)
fig.update_yaxes(title_text="Quantity (kWh/MWh)", row=2, col=1)
fig.update_yaxes(title_text="Correlation Coefficient", row=3, col=1, range=[-1, 1])

fig.update_layout(
    height=900,
    showlegend=True,
    hovermode='x unified'
)

st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# STATISTICS
# ============================================================================

st.subheader("📊 Correlation Statistics")

col1, col2, col3, col4 = st.columns(4)

mean_corr = correlation_df['correlation'].mean()
max_corr = correlation_df['correlation'].max()
min_corr = correlation_df['correlation'].min()
std_corr = correlation_df['correlation'].std()

with col1:
    st.metric("Mean Correlation", f"{mean_corr:.3f}")

with col2:
    st.metric("Max Correlation", f"{max_corr:.3f}")

with col3:
    st.metric("Min Correlation", f"{min_corr:.3f}")

with col4:
    st.metric("Std Dev", f"{std_corr:.3f}")

# Interpretation
st.subheader("📈 Interpretation")

if abs(mean_corr) > 0.7:
    strength = "Strong"
    color = "red" if mean_corr > 0 else "blue"
elif abs(mean_corr) > 0.4:
    strength = "Moderate"
    color = "orange"
else:
    strength = "Weak"
    color = "gray"

direction = "positive" if mean_corr > 0 else "negative"

st.markdown(f"""
**{strength}** {direction} correlation detected between **{weather_property.replace('_', ' ')}**
and **{data_type.lower()} ({energy_group})** in price area **{price_area}**.

- Mean correlation coefficient: **{mean_corr:.3f}**
- Window size: **{window_hours} hours** ({window_hours//24} days)
- Lag: **{lag_hours} hours** ({lag_hours//24:.1f} days)
""")

if lag_hours > 0:
    st.info(f"ℹ️ Positive lag of {lag_hours} hours means energy data lags weather by approximately {lag_hours/24:.1f} days")
elif lag_hours < 0:
    st.info(f"ℹ️ Negative lag of {lag_hours} hours means weather data lags energy by approximately {abs(lag_hours)/24:.1f} days")

# ============================================================================
# FINDINGS & OBSERVATIONS
# ============================================================================

with st.expander("🔍 Notable Patterns & Extreme Weather Events"):
    st.markdown("""
    ### Observations

    Use the correlation plot above to identify:

    1. **Sustained High Correlation Periods**:
       - Look for extended periods where |correlation| > 0.7
       - These indicate strong weather-energy relationships

    2. **Correlation Breakdowns**:
       - Sudden drops to near-zero correlation
       - May indicate system changes, outages, or unusual events

    3. **Seasonal Patterns**:
       - Compare winter vs summer correlations
       - Different energy sources respond differently to seasons

    4. **Extreme Weather Events**:
       - Sharp spikes or drops in correlation
       - Check the weather and energy plots for corresponding events

    ### Expected Relationships

    **Wind Production**:
    - Strong positive correlation with wind speed
    - Near-zero correlation with temperature

    **Hydro Production**:
    - Positive correlation with precipitation (lagged)
    - Seasonal temperature effects

    **Consumption**:
    - Negative correlation with temperature (heating demand)
    - Weather-independent baseline demand

    ### Analysis Tips

    - Adjust the **window size** to smooth or capture finer details
    - Use **lag** to explore delayed effects (e.g., precipitation → hydro after several days)
    - Compare different **price areas** to see regional differences
    """)

# ============================================================================
# DATA EXPORT
# ============================================================================

with st.expander("💾 Export Correlation Data"):
    st.markdown("Download the computed correlation time series for further analysis.")

    export_df = correlation_df.copy()
    export_df['weather_property'] = weather_property
    export_df['energy_type'] = data_type
    export_df['energy_group'] = energy_group
    export_df['price_area'] = price_area
    export_df['window_hours'] = window_hours
    export_df['lag_hours'] = lag_hours

    csv = export_df.to_csv(index=False)

    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"correlation_{price_area}_{weather_property}_{data_type}_{energy_group}.csv",
        mime="text/csv"
    )

# ============================================================================
# METHODOLOGY
# ============================================================================

with st.expander("ℹ️ Methodology - Sliding Window Correlation"):
    st.markdown("""
    ### Sliding Window Correlation Analysis

    This page uses a **sliding window** approach to compute time-varying correlation:

    1. **Data Alignment**:
       - Energy data from MongoDB (hourly aggregated)
       - Weather data from Open-Meteo API (hourly)
       - Merged on common timestamps

    2. **Lag Application**:
       - Positive lag: Energy data is shifted forward (energy lags weather)
       - Negative lag: Weather data is shifted forward (weather lags energy)
       - Useful for exploring delayed effects

    3. **Sliding Window**:
       - A window of specified size (e.g., 168 hours = 7 days) slides through the data
       - At each position, Pearson correlation is computed between weather and energy
       - Result: Time series of correlation coefficients

    4. **Interpretation**:
       - **r > 0.7**: Strong positive correlation
       - **0.4 < r < 0.7**: Moderate positive correlation
       - **-0.4 < r < 0.4**: Weak/no correlation
       - **-0.7 < r < -0.4**: Moderate negative correlation
       - **r < -0.7**: Strong negative correlation

    ### Price Area Coordinates

    Weather data is fetched for approximate centers of each price area:
    - **NO1** (Oslo): 60.0°N, 11.0°E
    - **NO2** (Kristiansand): 58.5°N, 7.5°E
    - **NO3** (Trondheim): 63.5°N, 10.5°E
    - **NO4** (Tromsø): 69.5°N, 19.0°E
    - **NO5** (Bergen): 60.5°N, 6.0°E

    ### Data Sources
    - **Energy**: Elhub via MongoDB Atlas (2021-2024)
    - **Weather**: Open-Meteo API (ERA5 reanalysis)
    """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("🌤️ Assessment 4 - Weather-Energy Correlation Analysis | Energy: Elhub MongoDB | Weather: Open-Meteo ERA5")
