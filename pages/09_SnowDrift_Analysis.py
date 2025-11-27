# pages/09_SnowDrift_Analysis.py
"""
Snow Drift Calculation and Visualization
Assessment 4 - New Feature

Based on Tabler (2003) methodology for calculating snow drifting.
Requires coordinates from the Map page and weather data from Open-Meteo API.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime
import sys
sys.path.append('..')

st.set_page_config(page_title="Snow Drift Analysis", page_icon="❄️", layout="wide")

# ============================================================================
# TITLE AND DESCRIPTION
# ============================================================================

st.title("❄️ Snow Drift Analysis (Tabler 2003)")
st.markdown("""
This page calculates annual snow drifting using the Tabler (2003) methodology.
Weather data is fetched from Open-Meteo API for the coordinates selected on the Map page.
""")

# ============================================================================
# CHECK IF COORDINATES ARE SELECTED
# ============================================================================

if 'selected_coords' not in st.session_state or st.session_state.selected_coords is None:
    st.warning("⚠️ No location selected!")
    st.info("""
    Please go to the **Map** page first and select a location by:
    1. Entering latitude and longitude coordinates
    2. Clicking the "Set Location" button

    Once you've selected a location, return to this page to perform snow drift analysis.
    """)

    # Provide manual override for testing
    with st.expander("🔧 Manual Coordinate Entry (For Testing)"):
        col1, col2 = st.columns(2)
        with col1:
            test_lat = st.number_input("Test Latitude", value=60.39, step=0.01)
        with col2:
            test_lon = st.number_input("Test Longitude", value=5.32, step=0.01)

        if st.button("Use Test Coordinates"):
            st.session_state.selected_coords = (test_lat, test_lon)
            st.rerun()

    st.stop()

# Get coordinates
lat, lon = st.session_state.selected_coords

st.success(f"📍 Using coordinates: {lat:.4f}°N, {lon:.4f}°E")
if 'selected_price_area' in st.session_state and st.session_state.selected_price_area:
    st.info(f"Price Area: **{st.session_state.selected_price_area}**")

# ============================================================================
# TABLER (2003) SNOW DRIFT FUNCTIONS
# ============================================================================

def compute_Qupot(hourly_wind_speeds, dt=3600):
    """
    Compute the potential wind-driven snow transport (Qupot) [kg/m]
    Formula: Qupot = sum((u^3.8) * dt) / 233847
    """
    total = sum((u ** 3.8) * dt for u in hourly_wind_speeds) / 233847
    return total

def sector_index(direction):
    """
    Given a wind direction in degrees, returns the index (0-15)
    corresponding to a 16-sector division.
    """
    return int(((direction + 11.25) % 360) // 22.5)

def compute_sector_transport(hourly_wind_speeds, hourly_wind_dirs, dt=3600):
    """
    Compute the cumulative transport for each of 16 wind sectors.
    Returns: A list of 16 transport values (kg/m)
    """
    sectors = [0.0] * 16
    for u, d in zip(hourly_wind_speeds, hourly_wind_dirs):
        idx = sector_index(d)
        sectors[idx] += ((u ** 3.8) * dt) / 233847
    return sectors

def compute_snow_transport(T, F, theta, Swe, hourly_wind_speeds, dt=3600):
    """
    Compute snow drifting transport according to Tabler (2003).

    Parameters:
      T: Maximum transport distance (m)
      F: Fetch distance (m)
      theta: Relocation coefficient
      Swe: Total snowfall water equivalent (mm)
      hourly_wind_speeds: list of wind speeds [m/s]

    Returns: Dictionary with transport components
    """
    Qupot = compute_Qupot(hourly_wind_speeds, dt)
    Qspot = 0.5 * T * Swe
    Srwe = theta * Swe

    if Qupot > Qspot:
        Qinf = 0.5 * T * Srwe
        control = "Snowfall controlled"
    else:
        Qinf = Qupot
        control = "Wind controlled"

    Qt = Qinf * (1 - 0.14 ** (F / T))

    return {
        "Qupot (kg/m)": Qupot,
        "Qspot (kg/m)": Qspot,
        "Srwe (mm)": Srwe,
        "Qinf (kg/m)": Qinf,
        "Qt (kg/m)": Qt,
        "Control": control
    }

def compute_fence_height(Qt, fence_type):
    """
    Calculate necessary fence height for storing snow drift.
    Storage capacity factors: Wyoming=8.5, Slat-and-wire=7.7, Solid=2.9
    """
    Qt_tonnes = Qt / 1000.0

    factors = {
        "Wyoming": 8.5,
        "Slat-and-wire": 7.7,
        "Solid": 2.9
    }

    factor = factors.get(fence_type, 8.5)
    H = (Qt_tonnes / factor) ** (1 / 2.2)
    return H

# ============================================================================
# FETCH WEATHER DATA FROM OPEN-METEO
# ============================================================================

@st.cache_data(ttl=3600)
def fetch_weather_data(latitude, longitude, start_year, end_year):
    """
    Fetch hourly weather data from Open-Meteo API.
    """
    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": f"{start_year}-01-01",
        "end_date": f"{end_year}-12-31",
        "hourly": ["temperature_2m", "precipitation", "wind_speed_10m", "wind_direction_10m"],
        "timezone": "UTC"
    }

    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()

        # Convert to DataFrame
        df = pd.DataFrame({
            'time': pd.to_datetime(data['hourly']['time']),
            'temperature_2m': data['hourly']['temperature_2m'],
            'precipitation': data['hourly']['precipitation'],
            'wind_speed_10m': data['hourly']['wind_speed_10m'],
            'wind_direction_10m': data['hourly']['wind_direction_10m']
        })

        # Define season: July 1 to June 30
        df['season'] = df['time'].apply(lambda dt: dt.year if dt.month >= 7 else dt.year - 1)

        return df

    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return None

# ============================================================================
# SIDEBAR CONTROLS
# ============================================================================

st.sidebar.header("Snow Drift Parameters")

# Year range selector
col1, col2 = st.sidebar.columns(2)
with col1:
    start_year = st.number_input("Start Year", min_value=2021, max_value=2023, value=2021, step=1)
with col2:
    end_year = st.number_input("End Year", min_value=2022, max_value=2024, value=2022, step=1)

if start_year > end_year:
    st.sidebar.error("Start year must be <= end year")
    st.stop()

# Tabler parameters
st.sidebar.subheader("Tabler (2003) Parameters")

T = st.sidebar.number_input(
    "Max Transport Distance (m)",
    min_value=100,
    max_value=10000,
    value=3000,
    step=100,
    help="Maximum transport distance in meters"
)

F = st.sidebar.number_input(
    "Fetch Distance (m)",
    min_value=1000,
    max_value=50000,
    value=30000,
    step=1000,
    help="Fetch distance in meters"
)

theta = st.sidebar.slider(
    "Relocation Coefficient",
    min_value=0.1,
    max_value=1.0,
    value=0.5,
    step=0.05,
    help="Relocation coefficient (θ)"
)

# Fence type selector
fence_type = st.sidebar.selectbox(
    "Fence Type",
    options=["Wyoming", "Slat-and-wire", "Solid"],
    help="Type of fence for height calculation"
)

# ============================================================================
# FETCH AND PROCESS DATA
# ============================================================================

with st.spinner(f"Fetching weather data from Open-Meteo API for {lat:.2f}°N, {lon:.2f}°E..."):
    weather_df = fetch_weather_data(lat, lon, start_year, end_year)

if weather_df is None:
    st.error("Failed to fetch weather data. Please try again or select different coordinates.")
    st.stop()

st.success(f"✅ Loaded {len(weather_df):,} hours of weather data ({start_year}-{end_year})")

# ============================================================================
# COMPUTE SNOW DRIFT PER SEASON
# ============================================================================

def compute_yearly_results(df, T, F, theta):
    """Compute yearly (seasonal) snow transport"""
    seasons = sorted(df['season'].unique())
    results_list = []

    for s in seasons:
        season_start = pd.Timestamp(year=s, month=7, day=1)
        season_end = pd.Timestamp(year=s+1, month=6, day=30, hour=23, minute=59)

        df_season = df[(df['time'] >= season_start) & (df['time'] <= season_end)].copy()

        if df_season.empty:
            continue

        # Calculate Swe: precipitation when temp < 1°C
        df_season['Swe_hourly'] = df_season.apply(
            lambda row: row['precipitation'] if row['temperature_2m'] < 1 else 0, axis=1
        )

        total_Swe = df_season['Swe_hourly'].sum()
        wind_speeds = df_season["wind_speed_10m"].tolist()

        result = compute_snow_transport(T, F, theta, total_Swe, wind_speeds)
        result["season"] = f"{s}-{s+1}"
        result["total_Swe"] = total_Swe

        # Compute fence height
        result["fence_height"] = compute_fence_height(result["Qt (kg/m)"], fence_type)

        results_list.append(result)

    return pd.DataFrame(results_list)

yearly_results = compute_yearly_results(weather_df, T, F, theta)

# ============================================================================
# DISPLAY RESULTS
# ============================================================================

st.subheader("📊 Annual Snow Drift Results")

if yearly_results.empty:
    st.warning("No seasonal data available for the selected year range.")
    st.stop()

# Summary metrics
col1, col2, col3, col4 = st.columns(4)

overall_avg = yearly_results['Qt (kg/m)'].mean()

with col1:
    st.metric(
        "Average Snow Drift",
        f"{overall_avg/1000:.1f} tonnes/m"
    )

with col2:
    max_drift = yearly_results['Qt (kg/m)'].max()
    st.metric(
        "Maximum (Season)",
        f"{max_drift/1000:.1f} tonnes/m"
    )

with col3:
    avg_height = yearly_results['fence_height'].mean()
    st.metric(
        f"Avg {fence_type} Height",
        f"{avg_height:.2f} m"
    )

with col4:
    total_swe = yearly_results['total_Swe'].mean()
    st.metric(
        "Avg Snowfall (SWE)",
        f"{total_swe:.0f} mm"
    )

# ============================================================================
# PLOT ANNUAL SNOW DRIFT
# ============================================================================

st.subheader("Annual Snow Drift Over Time")

fig_annual = go.Figure()

fig_annual.add_trace(go.Bar(
    x=yearly_results['season'],
    y=yearly_results['Qt (kg/m)'] / 1000,  # Convert to tonnes
    name='Snow Drift',
    marker_color='lightblue',
    hovertemplate='Season: %{x}<br>Drift: %{y:.1f} tonnes/m<extra></extra>'
))

# Add average line
fig_annual.add_hline(
    y=overall_avg / 1000,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Average: {overall_avg/1000:.1f} tonnes/m"
)

fig_annual.update_layout(
    xaxis_title="Season (July-June)",
    yaxis_title="Snow Drift (tonnes/m)",
    hovermode='x unified',
    height=400
)

st.plotly_chart(fig_annual, use_container_width=True)

# ============================================================================
# WIND ROSE PLOT
# ============================================================================

st.subheader("Wind Rose - Directional Snow Transport")

def compute_average_sector(df):
    """Compute average directional breakdown"""
    sectors_list = []

    for s in df['season'].unique():
        group = df[df['season'] == s].copy()
        group['Swe_hourly'] = group.apply(
            lambda row: row['precipitation'] if row['temperature_2m'] < 1 else 0, axis=1
        )

        ws = group["wind_speed_10m"].tolist()
        wdir = group["wind_direction_10m"].tolist()

        sectors = compute_sector_transport(ws, wdir)
        sectors_list.append(sectors)

    avg_sectors = np.mean(sectors_list, axis=0)
    return avg_sectors

avg_sectors = compute_average_sector(weather_df)

# Create wind rose (polar bar chart)
directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
              'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

angles = np.arange(0, 360, 360/16)

fig_rose = go.Figure()

fig_rose.add_trace(go.Barpolar(
    r=avg_sectors / 1000,  # Convert to tonnes
    theta=angles,
    width=[22.5] * 16,
    marker_color='lightblue',
    marker_line_color='black',
    marker_line_width=1,
    hovertemplate='Direction: %{theta}°<br>Transport: %{r:.2f} tonnes/m<extra></extra>'
))

fig_rose.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            title="Transport (tonnes/m)"
        ),
        angularaxis=dict(
            direction="clockwise",
            ticktext=directions,
            tickvals=angles
        )
    ),
    title=f"Average Directional Snow Transport<br>Overall: {overall_avg/1000:.1f} tonnes/m",
    height=500
)

st.plotly_chart(fig_rose, use_container_width=True)

# ============================================================================
# DETAILED RESULTS TABLE
# ============================================================================

with st.expander("📋 Detailed Results by Season"):
    display_df = yearly_results.copy()
    display_df['Qt (tonnes/m)'] = display_df['Qt (kg/m)'] / 1000
    display_df['Fence Height (m)'] = display_df['fence_height']

    columns_to_show = ['season', 'Qt (tonnes/m)', 'Control', 'total_Swe', 'Fence Height (m)']
    display_df = display_df[columns_to_show]
    display_df.columns = ['Season', 'Drift (tonnes/m)', 'Control Type', 'Snowfall (mm)', f'{fence_type} Height (m)']

    st.dataframe(
        display_df.style.format({
            'Drift (tonnes/m)': '{:.1f}',
            'Snowfall (mm)': '{:.0f}',
            f'{fence_type} Height (m)': '{:.2f}'
        }),
        use_container_width=True
    )

# ============================================================================
# METHODOLOGY EXPLANATION
# ============================================================================

with st.expander("ℹ️ Methodology (Tabler 2003)"):
    st.markdown("""
    ### Snow Drift Calculation (Tabler 2003)

    This analysis uses the Tabler (2003) methodology for calculating snow drifting:

    #### Key Components:

    1. **Qupot** (Potential wind-driven transport):
       - Calculated from hourly wind speeds using u³⁸
       - Represents the maximum possible snow transport

    2. **Qspot** (Snowfall-limited transport):
       - Based on total snowfall water equivalent (SWE)
       - SWE = precipitation when temperature < 1°C

    3. **Qinf** (Controlling transport):
       - If Qupot > Qspot: **Snowfall controlled**
       - Otherwise: **Wind controlled**

    4. **Qt** (Mean annual snow transport):
       - Final drift calculation considering fetch distance
       - Qt = Qinf × (1 - 0.14^(F/T))

    #### Season Definition:
    - Season runs from **July 1** to **June 30** (next year)
    - This captures the full winter snow accumulation period

    #### Fence Height Calculation:
    - H = (Qt_tonnes / factor)^(1/2.2)
    - Storage capacity factors:
      - Wyoming: 8.5
      - Slat-and-wire: 7.7
      - Solid: 2.9

    #### Data Source:
    - Weather data from Open-Meteo API (ERA5 reanalysis)
    - Hourly resolution: temperature, precipitation, wind speed/direction
    """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("❄️ Assessment 4 - Snow Drift Analysis (Tabler 2003) | Weather Data: Open-Meteo ERA5")
