"""
Assessment 4 - Meteorology-Energy Correlation Analysis
Sliding window correlation between weather variables and energy metrics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from pymongo import MongoClient
from scipy import stats

st.set_page_config(page_title="Correlation Analysis", page_icon="📊", layout="wide")

st.title("📊 Meteorology-Energy Correlation Analysis")

st.markdown("""
Analyze the relationship between meteorological conditions and energy production/consumption
using sliding window correlation.
""")


# MongoDB connection
@st.cache_resource
def get_mongo_client():
    """Connect to MongoDB"""
    mongo_uri = st.secrets.get("MONGO_URI", "mongodb+srv://ismasohail_user:IsmaMinhas@cluster0.e3wct64.mongodb.net/ind320?retryWrites=true&w=majority&appName=Cluster0")
    return MongoClient(mongo_uri)


# Fetch weather data
@st.cache_data(ttl=3600)
def fetch_weather_data(lat, lon, start_date, end_date):
    """Fetch daily weather data from Open-Meteo"""
    try:
        url = "https://archive-api.open-meteo.com/v1/archive"

        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "daily": "temperature_2m_mean,precipitation_sum,windspeed_10m_max,sunshine_duration",
            "timezone": "Europe/Oslo"
        }

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        df = pd.DataFrame({
            'date': pd.to_datetime(data['daily']['time']),
            'temperature': data['daily']['temperature_2m_mean'],
            'precipitation': data['daily']['precipitation_sum'],
            'windspeed': data['daily']['windspeed_10m_max'],
            'sunshine': data['daily']['sunshine_duration']
        })

        return df

    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return None


# Fetch energy data
@st.cache_data(ttl=3600)
def fetch_energy_data(price_area, start_date, end_date, metric_type):
    """Fetch daily aggregated energy data from MongoDB"""
    try:
        client = get_mongo_client()
        db = client["ind320"]

        # Determine collection based on year
        if start_date.year <= 2021 and end_date.year <= 2021:
            collection_name = f"elhub_{metric_type}_2021"
        else:
            collection_name = f"elhub_{metric_type}_2022_2024"

        collection = db[collection_name]

        # Query data
        query = {
            "priceArea": price_area,
            "startTime": {
                "$gte": datetime.combine(start_date, datetime.min.time()),
                "$lte": datetime.combine(end_date, datetime.max.time())
            }
        }

        data = list(collection.find(query))

        if not data:
            return None

        df = pd.DataFrame(data)

        # Aggregate to daily
        df['date'] = pd.to_datetime(df['startTime']).dt.date
        daily_df = df.groupby('date').agg({
            'quantityMWh': 'sum'
        }).reset_index()

        daily_df['date'] = pd.to_datetime(daily_df['date'])

        return daily_df

    except Exception as e:
        st.error(f"Error fetching energy data: {e}")
        return None


def calculate_sliding_correlation(series1, series2, window_size, lag=0):
    """
    Calculate sliding window correlation between two time series

    Parameters:
    - series1, series2: pandas Series
    - window_size: int, window size in days
    - lag: int, lag to apply to series2 (positive = series2 leads)

    Returns:
    - DataFrame with correlations
    """

    # Apply lag
    if lag > 0:
        series2_lagged = series2.shift(-lag)
    elif lag < 0:
        series2_lagged = series2.shift(abs(lag))
    else:
        series2_lagged = series2

    correlations = []
    dates = []

    for i in range(window_size, len(series1)):
        window1 = series1.iloc[i-window_size:i]
        window2 = series2_lagged.iloc[i-window_size:i]

        # Remove NaN values
        valid_mask = ~(window1.isna() | window2.isna())
        window1_clean = window1[valid_mask]
        window2_clean = window2[valid_mask]

        if len(window1_clean) > 3:  # Need at least 3 points
            corr, _ = stats.pearsonr(window1_clean, window2_clean)
            correlations.append(corr)
            dates.append(series1.index[i])
        else:
            correlations.append(np.nan)
            dates.append(series1.index[i])

    return pd.DataFrame({'date': dates, 'correlation': correlations})


# Sidebar controls
st.sidebar.header("Analysis Parameters")

# Price area selection
price_area = st.sidebar.selectbox(
    "Select Price Area:",
    options=["NO1", "NO2", "NO3", "NO4", "NO5"],
    index=0
)

# Date range
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "Start Date:",
        value=datetime(2021, 1, 1),
        min_value=datetime(2021, 1, 1),
        max_value=datetime(2024, 12, 31)
    )

with col2:
    end_date = st.date_input(
        "End Date:",
        value=datetime(2021, 12, 31),
        min_value=datetime(2021, 1, 1),
        max_value=datetime(2024, 12, 31)
    )

# Convert to datetime
start_datetime = datetime.combine(start_date, datetime.min.time())
end_datetime = datetime.combine(end_date, datetime.max.time())

# Meteorological variable
weather_var = st.sidebar.selectbox(
    "Meteorological Variable:",
    options=[
        ("Temperature (°C)", "temperature"),
        ("Precipitation (mm)", "precipitation"),
        ("Wind Speed (m/s)", "windspeed"),
        ("Sunshine Duration (s)", "sunshine")
    ],
    format_func=lambda x: x[0]
)

# Energy metric
metric_type = st.sidebar.radio(
    "Energy Metric:",
    options=["Production", "Consumption"]
)

# Correlation parameters
st.sidebar.subheader("Correlation Parameters")

window_size = st.sidebar.slider(
    "Window Size (days):",
    min_value=7,
    max_value=90,
    value=30,
    step=7,
    help="Size of sliding window for correlation calculation"
)

lag_days = st.sidebar.slider(
    "Lag (days):",
    min_value=-30,
    max_value=30,
    value=0,
    step=1,
    help="Positive: weather leads energy. Negative: energy leads weather."
)


# Get coordinates (use default if not set)
if 'clicked_lat' not in st.session_state or st.session_state.clicked_lat is None:
    # Use default coordinates for selected price area
    area_coords = {
        "NO1": (59.9139, 10.7522),  # Oslo
        "NO2": (58.1467, 7.9956),   # Kristiansand
        "NO3": (63.4305, 10.3951),  # Trondheim
        "NO4": (69.6492, 18.9553),  # Tromsø
        "NO5": (60.3929, 5.3241)    # Bergen
    }
    lat, lon = area_coords[price_area]
    st.info(f"Using default coordinates for {price_area}: ({lat:.4f}, {lon:.4f})")
else:
    lat = st.session_state.clicked_lat
    lon = st.session_state.clicked_lon
    st.success(f"Using selected location: ({lat:.4f}, {lon:.4f})")


# Fetch data
with st.spinner("Fetching data..."):
    # Fetch weather data
    weather_df = fetch_weather_data(lat, lon, start_date, end_date)

    # Fetch energy data
    energy_df = fetch_energy_data(
        price_area,
        start_date,
        end_date,
        metric_type.lower()
    )

if weather_df is None or weather_df.empty:
    st.error("Failed to fetch weather data.")
    st.stop()

if energy_df is None or energy_df.empty:
    st.error(f"No {metric_type.lower()} data found for {price_area} in the selected period.")
    st.stop()


# Merge datasets
merged_df = pd.merge(weather_df, energy_df, on='date', how='inner')

if merged_df.empty:
    st.error("No overlapping data found between weather and energy datasets.")
    st.stop()

st.success(f"Loaded {len(merged_df)} days of data")


# Display data statistics
st.subheader("Data Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Days Analyzed", len(merged_df))

with col2:
    st.metric(
        weather_var[0],
        f"{merged_df[weather_var[1]].mean():.2f}"
    )

with col3:
    st.metric(
        f"Avg {metric_type}",
        f"{merged_df['quantityMWh'].mean():.2f} MWh"
    )

with col4:
    st.metric(
        "Total Energy",
        f"{merged_df['quantityMWh'].sum():.0f} MWh"
    )


# Calculate correlation
with st.spinner("Calculating sliding window correlation..."):
    # Prepare series
    merged_df = merged_df.set_index('date').sort_index()

    weather_series = merged_df[weather_var[1]]
    energy_series = merged_df['quantityMWh']

    # Calculate sliding correlation
    corr_df = calculate_sliding_correlation(
        weather_series,
        energy_series,
        window_size,
        lag_days
    )


# Plot correlation over time
st.subheader(f"Sliding Window Correlation: {weather_var[0]} vs {metric_type}")

fig_corr = go.Figure()

fig_corr.add_trace(go.Scatter(
    x=corr_df['date'],
    y=corr_df['correlation'],
    mode='lines',
    name='Correlation',
    line=dict(color='blue', width=2),
    fill='tozeroy',
    fillcolor='rgba(0,0,255,0.1)'
))

# Add zero line
fig_corr.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="No Correlation")

# Add significance thresholds (approximate for n=window_size)
sig_threshold = 1.96 / np.sqrt(window_size)  # 95% confidence
fig_corr.add_hline(y=sig_threshold, line_dash="dot", line_color="green",
                  annotation_text="Positive Significance")
fig_corr.add_hline(y=-sig_threshold, line_dash="dot", line_color="red",
                  annotation_text="Negative Significance")

fig_corr.update_layout(
    title=f"{window_size}-day Window Correlation (Lag: {lag_days} days)",
    xaxis_title="Date",
    yaxis_title="Pearson Correlation Coefficient",
    height=400,
    hovermode='x unified',
    yaxis=dict(range=[-1, 1])
)

st.plotly_chart(fig_corr, use_container_width=True)


# Statistics
st.subheader("Correlation Statistics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Mean Correlation", f"{corr_df['correlation'].mean():.3f}")

with col2:
    st.metric("Max Correlation", f"{corr_df['correlation'].max():.3f}")

with col3:
    st.metric("Min Correlation", f"{corr_df['correlation'].min():.3f}")


# Scatter plot for current correlation
st.subheader("Scatter Plot (Most Recent Window)")

# Get most recent window
recent_window_start = merged_df.index[-window_size]
recent_window_data = merged_df.loc[recent_window_start:]

fig_scatter = go.Figure()

fig_scatter.add_trace(go.Scatter(
    x=recent_window_data[weather_var[1]],
    y=recent_window_data['quantityMWh'],
    mode='markers',
    marker=dict(size=8, color='blue', opacity=0.6),
    name='Data Points'
))

# Add trend line
z = np.polyfit(
    recent_window_data[weather_var[1]].dropna(),
    recent_window_data['quantityMWh'].dropna(),
    1
)
p = np.poly1d(z)
x_trend = np.linspace(
    recent_window_data[weather_var[1]].min(),
    recent_window_data[weather_var[1]].max(),
    100
)

fig_scatter.add_trace(go.Scatter(
    x=x_trend,
    y=p(x_trend),
    mode='lines',
    line=dict(color='red', width=2, dash='dash'),
    name='Trend Line'
))

recent_corr = corr_df.iloc[-1]['correlation'] if not corr_df.empty else 0

fig_scatter.update_layout(
    title=f"Scatter Plot (Last {window_size} days) - Correlation: {recent_corr:.3f}",
    xaxis_title=weather_var[0],
    yaxis_title=f"{metric_type} (MWh)",
    height=400
)

st.plotly_chart(fig_scatter, use_container_width=True)


# Time series comparison
st.subheader("Time Series Comparison")

# Normalize both series for comparison
weather_norm = (weather_series - weather_series.mean()) / weather_series.std()
energy_norm = (energy_series - energy_series.mean()) / energy_series.std()

fig_ts = go.Figure()

fig_ts.add_trace(go.Scatter(
    x=weather_series.index,
    y=weather_norm,
    name=weather_var[0] + " (normalized)",
    line=dict(color='green', width=1.5)
))

fig_ts.add_trace(go.Scatter(
    x=energy_series.index,
    y=energy_norm,
    name=f"{metric_type} (normalized)",
    line=dict(color='orange', width=1.5)
))

fig_ts.update_layout(
    title="Normalized Time Series Comparison",
    xaxis_title="Date",
    yaxis_title="Normalized Value (z-score)",
    height=400,
    hovermode='x unified'
)

st.plotly_chart(fig_ts, use_container_width=True)


# Information
with st.expander("ℹ️ How to Interpret Correlation Results"):
    st.markdown("""
    ### Correlation Coefficient

    **Range:** -1 to +1

    - **+1:** Perfect positive correlation
    - **0:** No correlation
    - **-1:** Perfect negative correlation

    ### Interpretation

    **Positive Correlation (+0.3 to +1.0):**
    - When weather variable increases, energy metric increases
    - Example: Higher temperatures → Higher cooling demand

    **Negative Correlation (-0.3 to -1.0):**
    - When weather variable increases, energy metric decreases
    - Example: Higher temperatures → Lower heating demand

    **Weak Correlation (-0.3 to +0.3):**
    - Little to no linear relationship
    - Other factors may be more important

    ### Lag Parameter

    - **Positive lag:** Weather changes lead energy changes
    - **Negative lag:** Energy changes lead weather changes
    - **Zero lag:** Simultaneous relationship

    ### Sliding Window

    - Shows how correlation changes over time
    - Useful for detecting seasonal patterns
    - Larger windows = smoother, more stable correlations
    - Smaller windows = more responsive to short-term changes

    ### Practical Applications

    - Identify which weather factors most affect energy demand
    - Predict energy needs based on weather forecasts
    - Optimize energy production based on weather patterns
    - Understand seasonal variations in energy-weather relationships
    """)


# Footer
st.markdown("---")
st.caption(f"Assessment 4 - IND320 | Analysis for {price_area} | Window: {window_size} days | Lag: {lag_days} days")
