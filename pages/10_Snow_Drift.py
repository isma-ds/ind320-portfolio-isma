"""
Assessment 4 - Snow Drift Calculation and Wind Rose Visualization
Calculate snow accumulation patterns based on wind and weather data
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests

st.set_page_config(page_title="Snow Drift Analysis", page_icon="❄️", layout="wide")

st.title("❄️ Snow Drift Analysis")

st.markdown("""
Calculate snow drift accumulation based on meteorological data.
Snow drift is the movement and accumulation of snow due to wind action.
""")


# Fetch weather data from Open-Meteo API
@st.cache_data(ttl=3600)
def fetch_weather_data(lat, lon, start_year, end_year):
    """Fetch hourly weather data from Open-Meteo API"""
    try:
        url = "https://archive-api.open-meteo.com/v1/archive"

        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": f"{start_year}-07-01",  # July 1st
            "end_date": f"{end_year}-06-30",      # June 30th
            "hourly": "temperature_2m,precipitation,snowfall,windspeed_10m,winddirection_10m",
            "timezone": "Europe/Oslo"
        }

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        # Convert to DataFrame
        df = pd.DataFrame({
            'timestamp': pd.to_datetime(data['hourly']['time']),
            'temperature': data['hourly']['temperature_2m'],
            'precipitation': data['hourly']['precipitation'],
            'snowfall': data['hourly']['snowfall'],
            'windspeed': data['hourly']['windspeed_10m'],
            'winddirection': data['hourly']['winddirection_10m']
        })

        return df

    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return None


def compute_Qupot(hourly_wind_speeds, dt=3600):
    """
    Compute the potential wind-driven snow transport (Qupot) [kg/m]
    by summing hourly contributions using u^3.8.

    Formula from Tabler (2003):
       Qupot = sum((u^3.8) * dt) / 233847

    Parameters:
        hourly_wind_speeds: array of wind speeds [m/s]
        dt: time step in seconds (default 3600 for hourly data)

    Returns:
        float: Potential wind-driven transport [kg/m]
    """
    total = sum((u**3.8) * dt for u in hourly_wind_speeds) / 233847
    return total


def sector_index(direction):
    """
    Given a wind direction in degrees, returns the index (0-15)
    corresponding to a 16-sector division.
    """
    # Center the bin by adding 11.25 degrees then modulo 360 and divide by 22.5 degrees
    return int(((direction + 11.25) % 360) // 22.5)


def compute_sector_transport(hourly_wind_speeds, hourly_wind_dirs, dt=3600):
    """
    Compute the cumulative transport for each of 16 wind sectors.

    Parameters:
        hourly_wind_speeds: list of wind speeds [m/s]
        hourly_wind_dirs: list of wind directions [degrees]
        dt: time step in seconds

    Returns:
        A list of 16 transport values (kg/m) corresponding to the sectors.
    """
    sectors = [0.0] * 16
    for u, d in zip(hourly_wind_speeds, hourly_wind_dirs):
        idx = sector_index(d)
        sectors[idx] += ((u**3.8) * dt) / 233847
    return sectors


def calculate_snow_drift(df, T=3000, F=30000, theta=0.5):
    """
    Calculate snow drift using Tabler (2003) methodology.

    This implements the complete Tabler (2003) snow drift calculation including:
    - Potential wind-driven transport (Qupot)
    - Snowfall-limited transport (Qspot)
    - Relocated water equivalent (Srwe)
    - Mean annual snow transport (Qt)

    Parameters:
        df: DataFrame with hourly weather data
        T: Maximum transport distance (m) - default 3000m
        F: Fetch distance (m) - default 30000m
        theta: Relocation coefficient - default 0.5

    Returns:
        DataFrame with added columns:
            - Swe_hourly: Hourly snow water equivalent [mm]
            - wind_transport: Hourly wind transport contribution [kg/m]
            - snow_drift: Cumulative snow drift [kg/m]
    """

    # Calculate hourly Swe: precipitation counts when temperature < +1 degrees C
    df['Swe_hourly'] = df.apply(
        lambda row: row['precipitation'] if row['temperature'] < 1 else 0,
        axis=1
    )

    # Calculate total Swe for the period
    total_Swe = df['Swe_hourly'].sum()

    # Get wind speeds as list
    wind_speeds = df['windspeed'].tolist()

    # Calculate Qupot (potential wind-driven transport)
    Qupot = compute_Qupot(wind_speeds, dt=3600)

    # Calculate Qspot (snowfall-limited transport)
    Qspot = 0.5 * T * total_Swe

    # Calculate Srwe (relocated water equivalent)
    Srwe = theta * total_Swe

    # Determine controlling process
    if Qupot > Qspot:
        Qinf = 0.5 * T * Srwe
        control = "Snowfall controlled"
    else:
        Qinf = Qupot
        control = "Wind controlled"

    # Calculate Qt (mean annual snow transport)
    Qt = Qinf * (1 - 0.14 ** (F / T))

    # Calculate hourly wind transport contributions for visualization
    df['wind_transport'] = ((df['windspeed']**3.8) * 3600) / 233847

    # Calculate cumulative snow drift
    df['snow_drift'] = df['wind_transport'].cumsum()

    # Store metadata
    df.attrs['Qupot'] = Qupot
    df.attrs['Qspot'] = Qspot
    df.attrs['Srwe'] = Srwe
    df.attrs['Qinf'] = Qinf
    df.attrs['Qt'] = Qt
    df.attrs['control'] = control
    df.attrs['total_Swe'] = total_Swe

    return df


def create_wind_rose(df):
    """Create wind rose diagram showing wind direction frequencies"""

    # Define direction bins (16 compass directions)
    direction_bins = np.arange(0, 360, 22.5)
    direction_labels = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                       'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

    # Bin wind directions
    df['direction_bin'] = pd.cut(
        df['winddirection'],
        bins=np.append(direction_bins, 360),
        labels=direction_labels,
        include_lowest=True
    )

    # Count frequencies
    direction_counts = df['direction_bin'].value_counts().sort_index()

    # Create polar bar chart
    fig = go.Figure()

    fig.add_trace(go.Barpolar(
        r=direction_counts.values,
        theta=direction_labels,
        marker=dict(
            color=direction_counts.values,
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title="Frequency")
        ),
        hovertemplate='%{theta}<br>Count: %{r}<extra></extra>'
    ))

    fig.update_layout(
        title="Wind Rose Diagram",
        polar=dict(
            radialaxis=dict(showticklabels=True, ticks=''),
            angularaxis=dict(direction="clockwise")
        ),
        height=500
    )

    return fig


# Check if coordinates are set
if 'clicked_lat' not in st.session_state or st.session_state.clicked_lat is None:
    st.warning("⚠️ No location selected. Please select coordinates on the Interactive Map page first.")

    # Allow manual input as fallback
    st.subheader("Or Enter Coordinates Manually")

    col1, col2 = st.columns(2)
    with col1:
        manual_lat = st.number_input("Latitude:", min_value=58.0, max_value=71.0, value=60.0, step=0.1)
    with col2:
        manual_lon = st.number_input("Longitude:", min_value=4.0, max_value=31.0, value=10.0, step=0.1)

    if st.button("Use These Coordinates"):
        st.session_state.clicked_lat = manual_lat
        st.session_state.clicked_lon = manual_lon
        st.success("Coordinates set!")
        st.rerun()

    st.stop()


# Get coordinates from session state
lat = st.session_state.clicked_lat
lon = st.session_state.clicked_lon

st.success(f"Using location: ({lat:.4f}, {lon:.4f})")


# Sidebar controls
st.sidebar.header("Analysis Parameters")

# Year range selection
current_year = datetime.now().year
min_year = 2021
max_year = min(2024, current_year)

year_range = st.sidebar.slider(
    "Select Year Range:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, min(min_year + 1, max_year)),
    step=1
)

start_year, end_year = year_range

# Note about year definition
st.sidebar.info(f"""
**Year Definition:**
- 1 year = July 1 to June 30
- {start_year} means July 1, {start_year} to June 30, {start_year + 1}
""")


# Fetch weather data
with st.spinner(f"Fetching meteorological data for {start_year}-{end_year}..."):
    weather_df = fetch_weather_data(lat, lon, start_year, end_year)

if weather_df is None or weather_df.empty:
    st.error("Failed to fetch weather data. Please try different coordinates or year range.")
    st.stop()


# Calculate snow drift
with st.spinner("Calculating snow drift..."):
    weather_df = calculate_snow_drift(weather_df)


# Display Tabler (2003) statistics
st.subheader("Snow Transport Analysis (Tabler 2003)")

# Get stored metadata
Qt = weather_df.attrs.get('Qt', 0)
Qupot = weather_df.attrs.get('Qupot', 0)
Qspot = weather_df.attrs.get('Qspot', 0)
control = weather_df.attrs.get('control', 'Unknown')
total_Swe = weather_df.attrs.get('total_Swe', 0)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Mean Annual Snow Transport (Qt)", f"{Qt/1000:.1f} tonnes/m")

with col2:
    st.metric("Total Snow Water Equiv (Swe)", f"{total_Swe:.2f} mm")

with col3:
    st.metric("Potential Transport (Qupot)", f"{Qupot:.0f} kg/m")

with col4:
    st.metric("Process Control", control)

# Additional weather stats
st.subheader("Weather Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Snowfall", f"{weather_df['snowfall'].sum():.2f} mm")

with col2:
    st.metric("Total Precipitation", f"{weather_df['precipitation'].sum():.2f} mm")

with col3:
    st.metric("Avg Wind Speed", f"{weather_df['windspeed'].mean():.2f} m/s")

with col4:
    st.metric("Avg Temperature", f"{weather_df['temperature'].mean():.2f} °C")


# Calculate yearly snow drift
st.subheader("Yearly Snow Drift")

# Define water years (July to June)
weather_df['water_year'] = weather_df['timestamp'].apply(
    lambda x: x.year if x.month < 7 else x.year + 1
)

yearly_drift = weather_df.groupby('water_year').agg({
    'snow_drift': 'sum',
    'snowfall': 'sum',
    'windspeed': 'mean',
    'temperature': 'mean'
}).reset_index()

# Display yearly table
st.dataframe(
    yearly_drift.rename(columns={
        'water_year': 'Water Year',
        'snow_drift': 'Total Snow Drift (mm)',
        'snowfall': 'Total Snowfall (mm)',
        'windspeed': 'Avg Wind Speed (m/s)',
        'temperature': 'Avg Temperature (°C)'
    }),
    use_container_width=True
)


# Plot yearly snow drift
fig_yearly = go.Figure()

fig_yearly.add_trace(go.Bar(
    x=yearly_drift['water_year'],
    y=yearly_drift['snow_drift'],
    name='Snow Drift',
    marker_color='lightblue'
))

fig_yearly.add_trace(go.Scatter(
    x=yearly_drift['water_year'],
    y=yearly_drift['snowfall'],
    name='Total Snowfall',
    yaxis='y2',
    line=dict(color='darkblue', width=2)
))

fig_yearly.update_layout(
    title=f"Snow Drift by Water Year ({start_year}-{end_year})",
    xaxis_title="Water Year (July-June)",
    yaxis_title="Snow Drift (mm)",
    yaxis2=dict(
        title="Snowfall (mm)",
        overlaying='y',
        side='right'
    ),
    height=400,
    hovermode='x unified',
    legend=dict(x=0.01, y=0.99)
)

st.plotly_chart(fig_yearly, use_container_width=True)


# Wind Rose with Directional Transport
st.subheader("Wind Rose with Directional Snow Transport")

# Calculate sector-wise transport
ws = weather_df['windspeed'].tolist()
wdir = weather_df['winddirection'].tolist()
sectors = compute_sector_transport(ws, wdir)

# Convert to tonnes/m
sectors_tonnes = [s / 1000.0 for s in sectors]

# Create directional wind rose
direction_labels = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                   'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

fig_wind_transport = go.Figure()

fig_wind_transport.add_trace(go.Barpolar(
    r=sectors_tonnes,
    theta=direction_labels,
    marker=dict(
        color=sectors_tonnes,
        colorscale='Blues',
        showscale=True,
        colorbar=dict(title="Transport<br>(tonnes/m)")
    ),
    hovertemplate='%{theta}<br>Transport: %{r:.2f} tonnes/m<extra></extra>'
))

fig_wind_transport.update_layout(
    title=f"Directional Snow Transport Distribution<br>Total Qt: {Qt/1000:.1f} tonnes/m",
    polar=dict(
        radialaxis=dict(showticklabels=True, ticks=''),
        angularaxis=dict(direction="clockwise")
    ),
    height=500
)

st.plotly_chart(fig_wind_transport, use_container_width=True)

st.markdown("""
The wind rose shows snow transport by direction using Tabler (2003) formulas.
Each sector represents the cumulative wind-driven transport from that direction.
Prevailing wind directions contribute most to snow drift patterns.
""")


# Monthly breakdown
st.subheader("Monthly Snow Drift Breakdown")

weather_df['month'] = weather_df['timestamp'].dt.month
weather_df['year'] = weather_df['water_year']

monthly_drift = weather_df.groupby(['year', 'month'])['snow_drift'].sum().reset_index()

# Create month names
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

fig_monthly = go.Figure()

for year in sorted(monthly_drift['year'].unique()):
    year_data = monthly_drift[monthly_drift['year'] == year]

    fig_monthly.add_trace(go.Bar(
        x=[month_names[m-1] for m in year_data['month']],
        y=year_data['snow_drift'],
        name=f"Year {year}",
        hovertemplate='%{x}<br>%{y:.2f} mm<extra></extra>'
    ))

fig_monthly.update_layout(
    title="Monthly Snow Drift Comparison",
    xaxis_title="Month",
    yaxis_title="Snow Drift (mm)",
    height=400,
    barmode='group',
    hovermode='x unified'
)

st.plotly_chart(fig_monthly, use_container_width=True)


# Daily time series for selected year
st.subheader("Daily Snow Drift Time Series")

selected_year = st.selectbox(
    "Select Water Year:",
    options=sorted(yearly_drift['water_year'].unique()),
    index=0
)

year_data = weather_df[weather_df['water_year'] == selected_year].copy()
year_data['date'] = year_data['timestamp'].dt.date
daily_data = year_data.groupby('date').agg({
    'snow_drift': 'sum',
    'snowfall': 'sum',
    'windspeed': 'mean'
}).reset_index()

fig_daily = go.Figure()

fig_daily.add_trace(go.Scatter(
    x=daily_data['date'],
    y=daily_data['snow_drift'].cumsum(),
    name='Cumulative Snow Drift',
    fill='tozeroy',
    line=dict(color='lightblue', width=2)
))

fig_daily.add_trace(go.Scatter(
    x=daily_data['date'],
    y=daily_data['snowfall'].cumsum(),
    name='Cumulative Snowfall',
    line=dict(color='darkblue', width=2, dash='dash')
))

fig_daily.update_layout(
    title=f"Cumulative Snow Drift - Water Year {selected_year}",
    xaxis_title="Date",
    yaxis_title="Cumulative (mm)",
    height=400,
    hovermode='x unified',
    legend=dict(x=0.01, y=0.99)
)

st.plotly_chart(fig_daily, use_container_width=True)


# Information
with st.expander("ℹ️ About Tabler (2003) Snow Drift Methodology"):
    st.markdown("""
    ### Tabler (2003) Snow Drift Calculations

    This page implements the complete snow drift calculation methodology from Tabler (2003).

    **Key Parameters:**

    1. **Qupot (Potential Wind-Driven Transport):**
       - Formula: sum((u^3.8) * dt) / 233847
       - Based on hourly wind speed data
       - Represents maximum possible transport by wind

    2. **Qspot (Snowfall-Limited Transport):**
       - Formula: 0.5 * T * Swe
       - T = Maximum transport distance (3000m default)
       - Swe = Snow Water Equivalent (total snowfall when temp < 1C)

    3. **Srwe (Relocated Water Equivalent):**
       - Formula: theta * Swe
       - theta = Relocation coefficient (0.5 default)

    4. **Qinf (Controlling Transport):**
       - If Qupot > Qspot: Qinf = 0.5 * T * Srwe (snowfall controlled)
       - Otherwise: Qinf = Qupot (wind controlled)

    5. **Qt (Mean Annual Snow Transport):**
       - Formula: Qinf * (1 - 0.14^(F/T))
       - F = Fetch distance (30000m default)
       - Final result in tonnes/m

    **Wind Rose:**
    - 16-sector directional analysis
    - Shows cumulative transport from each direction
    - Uses same u^3.8 wind power formula

    **Water Year:**
    - Defined as July 1 to June 30
    - Matches Norwegian snow season
    - Allows complete winter cycle analysis

    **Data Source:** Open-Meteo ERA5 reanalysis

    **Reference:** Tabler, R.D. (2003). Controlling Blowing and Drifting Snow with Snow Fences and Road Design.
    """)


# Footer
st.markdown("---")
st.caption(f"Assessment 4 - IND320 | Location: ({lat:.4f}, {lon:.4f}) | Data: Open-Meteo ERA5")
