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


def calculate_snow_drift(df):
    """
    Calculate snow drift based on meteorological parameters

    Snow drift formula (simplified):
    drift = snowfall * wind_factor * temperature_factor

    Where:
    - wind_factor depends on wind speed (higher speed = more drift)
    - temperature_factor depends on temperature (colder = more cohesive)
    """

    # Wind drift factor: exponential relationship with wind speed
    # Drift starts at ~3 m/s and increases rapidly
    df['wind_factor'] = np.where(
        df['windspeed'] < 3,
        0,  # No drift below 3 m/s
        np.minimum((df['windspeed'] - 3) ** 1.5 / 10, 5)  # Cap at 5x
    )

    # Temperature factor: snow drifts more when it's cold and dry
    # Optimal drift: -5°C to -15°C
    df['temp_factor'] = np.where(
        df['temperature'] > 0,
        0.1,  # Wet snow, less drift
        np.where(
            df['temperature'] < -15,
            0.5,  # Very cold, crystals don't bind well
            1.0 + (df['temperature'] + 5) / 10  # Optimal range
        )
    )

    # Calculate snow drift (mm of snow equivalent)
    df['snow_drift'] = df['snowfall'] * df['wind_factor'] * df['temp_factor']

    # Ensure non-negative
    df['snow_drift'] = df['snow_drift'].clip(lower=0)

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


# Display statistics
st.subheader("Weather Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Snowfall", f"{weather_df['snowfall'].sum():.2f} mm")

with col2:
    st.metric("Total Snow Drift", f"{weather_df['snow_drift'].sum():.2f} mm")

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


# Wind Rose
st.subheader("Wind Rose Diagram")

wind_rose_fig = create_wind_rose(weather_df)
st.plotly_chart(wind_rose_fig, use_container_width=True)

st.markdown("""
The wind rose shows the frequency of wind from different directions.
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
with st.expander("ℹ️ About Snow Drift Calculations"):
    st.markdown("""
    ### Snow Drift Physics

    Snow drift is the transport of snow by wind. The calculations use:

    **Wind Factor:**
    - Drift starts at wind speeds above 3 m/s
    - Increases exponentially with wind speed
    - Higher winds = more snow movement

    **Temperature Factor:**
    - Optimal drift: -5°C to -15°C
    - Warmer (wet snow): Less drift
    - Very cold (<-15°C): Crystals don't bind well

    **Formula:**
    ```
    Snow Drift = Snowfall × Wind Factor × Temperature Factor
    ```

    **Water Year:**
    - Defined as July 1 to June 30
    - Matches Norwegian snow season
    - Allows complete winter cycle analysis

    **Data Source:** Open-Meteo ERA5 reanalysis
    """)


# Footer
st.markdown("---")
st.caption(f"Assessment 4 - IND320 | Location: ({lat:.4f}, {lon:.4f}) | Data: Open-Meteo ERA5")
