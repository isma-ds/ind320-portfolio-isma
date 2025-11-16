"""
Assessment 4 - SARIMAX Forecasting for Energy Production/Consumption
Time series forecasting with seasonal patterns and exogenous variables
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from pymongo import MongoClient
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="SARIMAX Forecasting", page_icon="🔮", layout="wide")

st.title("🔮 SARIMAX Energy Forecasting")

st.markdown("""
Forecast energy production or consumption using SARIMAX (Seasonal AutoRegressive Integrated Moving Average with eXogenous variables).
""")


# MongoDB connection
@st.cache_resource
def get_mongo_client():
    mongo_uri = st.secrets.get("MONGO_URI", "mongodb+srv://ismasohail_user:IsmaMinhas@cluster0.e3wct64.mongodb.net/ind320?retryWrites=true&w=majority&appName=Cluster0")
    return MongoClient(mongo_uri)


# Fetch energy data
@st.cache_data(ttl=3600)
def fetch_energy_data(price_area, group, start_date, end_date, metric_type):
    """Fetch daily aggregated energy data"""
    try:
        client = get_mongo_client()
        db = client["ind320"]

        if start_date.year <= 2021 and end_date.year <= 2021:
            collection_name = f"elhub_{metric_type}_2021"
        else:
            collection_name = f"elhub_{metric_type}_2022_2024"

        collection = db[collection_name]

        group_field = "productionGroup" if metric_type == "production" else "consumptionGroup"

        query = {
            "priceArea": price_area,
            group_field: group,
            "startTime": {
                "$gte": datetime.combine(start_date, datetime.min.time()),
                "$lte": datetime.combine(end_date, datetime.max.time())
            }
        }

        data = list(collection.find(query))

        if not data:
            return None

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['startTime']).dt.date
        daily_df = df.groupby('date').agg({'quantityMWh': 'sum'}).reset_index()
        daily_df['date'] = pd.to_datetime(daily_df['date'])

        return daily_df

    except Exception as e:
        st.error(f"Error fetching energy data: {e}")
        return None


# Fetch weather data
@st.cache_data(ttl=3600)
def fetch_weather_data(lat, lon, start_date, end_date):
    """Fetch weather data for exogenous variables"""
    try:
        url = "https://archive-api.open-meteo.com/v1/archive"

        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "daily": "temperature_2m_mean,precipitation_sum,windspeed_10m_max",
            "timezone": "Europe/Oslo"
        }

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        df = pd.DataFrame({
            'date': pd.to_datetime(data['daily']['time']),
            'temperature': data['daily']['temperature_2m_mean'],
            'precipitation': data['daily']['precipitation_sum'],
            'windspeed': data['daily']['windspeed_10m_max']
        })

        return df

    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return None


# Sidebar controls
st.sidebar.header("Forecasting Parameters")

# Price area and group selection
price_area = st.sidebar.selectbox("Price Area:", ["NO1", "NO2", "NO3", "NO4", "NO5"])

metric_type = st.sidebar.radio("Energy Metric:", ["Production", "Consumption"])

if metric_type == "Production":
    groups = ["Hydro", "Wind", "Thermal", "Solar"]
else:
    groups = ["Residential", "Commercial", "Industrial", "Other"]

selected_group = st.sidebar.selectbox(f"{metric_type} Group:", groups)


# Training data period
st.sidebar.subheader("Training Data Period")

train_start = st.sidebar.date_input(
    "Training Start:",
    value=datetime(2021, 1, 1),
    min_value=datetime(2021, 1, 1),
    max_value=datetime(2024, 6, 30)
)

train_end = st.sidebar.date_input(
    "Training End:",
    value=datetime(2021, 12, 31),
    min_value=datetime(2021, 1, 1),
    max_value=datetime(2024, 12, 31)
)


# SARIMAX parameters
st.sidebar.subheader("SARIMAX Parameters")

st.sidebar.markdown("**Non-Seasonal (p,d,q)**")
p = st.sidebar.slider("AR order (p):", 0, 5, 1, help="Autoregressive order")
d = st.sidebar.slider("Differencing (d):", 0, 2, 1, help="Degree of differencing")
q = st.sidebar.slider("MA order (q):", 0, 5, 1, help="Moving average order")

st.sidebar.markdown("**Seasonal (P,D,Q,s)**")
P = st.sidebar.slider("Seasonal AR (P):", 0, 2, 1)
D = st.sidebar.slider("Seasonal Diff (D):", 0, 1, 1)
Q = st.sidebar.slider("Seasonal MA (Q):", 0, 2, 1)
s = st.sidebar.selectbox("Seasonal Period (s):", [7, 30, 365], index=1, help="7=weekly, 30=monthly, 365=yearly")

# Forecast horizon
forecast_days = st.sidebar.slider("Forecast Horizon (days):", 7, 90, 30, step=7)

# Exogenous variables
st.sidebar.subheader("Exogenous Variables")
use_exog = st.sidebar.checkbox("Include Weather Variables", value=True)

if use_exog:
    exog_vars = st.sidebar.multiselect(
        "Select Variables:",
        ["temperature", "precipitation", "windspeed"],
        default=["temperature"]
    )
else:
    exog_vars = []


# Get coordinates
if 'clicked_lat' not in st.session_state or st.session_state.clicked_lat is None:
    area_coords = {
        "NO1": (59.9139, 10.7522), "NO2": (58.1467, 7.9956),
        "NO3": (63.4305, 10.3951), "NO4": (69.6492, 18.9553),
        "NO5": (60.3929, 5.3241)
    }
    lat, lon = area_coords[price_area]
else:
    lat, lon = st.session_state.clicked_lat, st.session_state.clicked_lon


# Fetch data
with st.spinner("Fetching training data..."):
    energy_df = fetch_energy_data(
        price_area, selected_group, train_start, train_end, metric_type.lower()
    )

if energy_df is None or energy_df.empty:
    st.error(f"No {metric_type.lower()} data found for {price_area} - {selected_group}")
    st.stop()

# Fetch weather data if using exogenous variables
if use_exog and exog_vars:
    forecast_end = train_end + timedelta(days=forecast_days)

    with st.spinner("Fetching weather data..."):
        weather_df = fetch_weather_data(lat, lon, train_start, forecast_end)

    if weather_df is None or weather_df.empty:
        st.warning("Weather data not available. Proceeding without exogenous variables.")
        use_exog = False
        exog_vars = []
    else:
        # Merge with energy data
        energy_df = pd.merge(energy_df, weather_df, on='date', how='left')


# Prepare time series
energy_df = energy_df.set_index('date').sort_index()
y_train = energy_df['quantityMWh']

# Prepare exogenous variables
if use_exog and exog_vars:
    X_train = energy_df[exog_vars].fillna(method='ffill')
    X_train = X_train.fillna(method='bfill')  # Handle any remaining NaN
else:
    X_train = None


# Display data statistics
st.subheader("Training Data Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Training Days", len(y_train))

with col2:
    st.metric("Mean Value", f"{y_train.mean():.2f} MWh")

with col3:
    st.metric("Std Dev", f"{y_train.std():.2f} MWh")

with col4:
    st.metric("Total Energy", f"{y_train.sum():.0f} MWh")


# Plot training data
fig_train = go.Figure()

fig_train.add_trace(go.Scatter(
    x=y_train.index,
    y=y_train.values,
    mode='lines',
    name='Training Data',
    line=dict(color='blue', width=1.5)
))

fig_train.update_layout(
    title=f"Training Data: {price_area} - {selected_group} {metric_type}",
    xaxis_title="Date",
    yaxis_title=f"{metric_type} (MWh)",
    height=300,
    hovermode='x unified'
)

st.plotly_chart(fig_train, use_container_width=True)


# Fit SARIMAX model
st.subheader("Model Training")

if st.button("Train Model and Generate Forecast", type="primary"):
    with st.spinner("Training SARIMAX model... This may take a moment."):
        try:
            # Define model
            model = SARIMAX(
                y_train,
                exog=X_train,
                order=(p, d, q),
                seasonal_order=(P, D, Q, s),
                enforce_stationarity=False,
                enforce_invertibility=False
            )

            # Fit model
            results = model.fit(disp=False, maxiter=200)

            st.success("Model trained successfully!")

            # Store in session state
            st.session_state.sarimax_results = results
            st.session_state.sarimax_params = {
                'p': p, 'd': d, 'q': q, 'P': P, 'D': D, 'Q': Q, 's': s,
                'price_area': price_area, 'group': selected_group,
                'metric_type': metric_type, 'forecast_days': forecast_days,
                'use_exog': use_exog, 'exog_vars': exog_vars
            }

            # Model summary
            with st.expander("📋 Model Summary"):
                st.text(results.summary())

            # Generate forecast
            st.subheader("Forecast Results")

            # Prepare exogenous variables for forecast period
            if use_exog and exog_vars:
                forecast_dates = pd.date_range(
                    start=y_train.index[-1] + timedelta(days=1),
                    periods=forecast_days,
                    freq='D'
                )

                # Get weather forecast (from existing weather data)
                X_forecast = weather_df[weather_df['date'].isin(forecast_dates)][exog_vars]
                X_forecast = X_forecast.fillna(method='ffill').fillna(method='bfill')
            else:
                X_forecast = None

            # Generate forecast
            forecast = results.get_forecast(steps=forecast_days, exog=X_forecast)
            forecast_mean = forecast.predicted_mean
            forecast_ci = forecast.conf_int(alpha=0.05)  # 95% confidence interval

            # Plot forecast
            fig_forecast = go.Figure()

            # Historical data
            fig_forecast.add_trace(go.Scatter(
                x=y_train.index,
                y=y_train.values,
                mode='lines',
                name='Historical',
                line=dict(color='blue', width=2)
            ))

            # Forecast
            fig_forecast.add_trace(go.Scatter(
                x=forecast_mean.index,
                y=forecast_mean.values,
                mode='lines',
                name='Forecast',
                line=dict(color='red', width=2, dash='dash')
            ))

            # Confidence interval
            fig_forecast.add_trace(go.Scatter(
                x=forecast_ci.index.tolist() + forecast_ci.index.tolist()[::-1],
                y=forecast_ci.iloc[:, 1].tolist() + forecast_ci.iloc[:, 0].tolist()[::-1],
                fill='toself',
                fillcolor='rgba(255, 0, 0, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='95% Confidence Interval',
                showlegend=True
            ))

            fig_forecast.update_layout(
                title=f"SARIMAX Forecast: {price_area} - {selected_group} {metric_type}",
                xaxis_title="Date",
                yaxis_title=f"{metric_type} (MWh)",
                height=500,
                hovermode='x unified'
            )

            st.plotly_chart(fig_forecast, use_container_width=True)

            # Forecast statistics
            st.subheader("Forecast Statistics")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Forecast Mean", f"{forecast_mean.mean():.2f} MWh")

            with col2:
                st.metric("Forecast Total", f"{forecast_mean.sum():.0f} MWh")

            with col3:
                st.metric("Uncertainty Range", f"±{(forecast_ci.iloc[:, 1] - forecast_mean).mean():.2f} MWh")

            # Forecast table
            st.subheader("Detailed Forecast")

            forecast_df = pd.DataFrame({
                'Date': forecast_mean.index,
                'Forecast (MWh)': forecast_mean.values,
                'Lower Bound (MWh)': forecast_ci.iloc[:, 0].values,
                'Upper Bound (MWh)': forecast_ci.iloc[:, 1].values
            })

            st.dataframe(forecast_df, use_container_width=True, height=300)

            # Model diagnostics
            with st.expander("📊 Model Diagnostics"):
                st.markdown("### AIC and BIC")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("AIC", f"{results.aic:.2f}")
                with col2:
                    st.metric("BIC", f"{results.bic:.2f}")

                st.markdown("Lower values indicate better model fit.")

        except Exception as e:
            st.error(f"Error training model: {e}")
            st.info("Try adjusting the parameters or using a different time period.")

else:
    st.info("👆 Click the button above to train the model and generate forecast")


# Information
with st.expander("ℹ️ About SARIMAX Forecasting"):
    st.markdown("""
    ### SARIMAX Components

    **SARIMA** = Seasonal AutoRegressive Integrated Moving Average
    **X** = eXogenous variables (external factors like weather)

    ### Parameters

    **Non-Seasonal (p, d, q):**
    - **p (AR):** Number of lag observations
    - **d (I):** Degree of differencing (make data stationary)
    - **q (MA):** Size of moving average window

    **Seasonal (P, D, Q, s):**
    - **P:** Seasonal autoregressive order
    - **D:** Seasonal differencing
    - **Q:** Seasonal moving average order
    - **s:** Season length (7=weekly, 30=monthly, 365=yearly)

    ### Exogenous Variables

    External factors that influence the forecast:
    - Temperature
    - Precipitation
    - Wind speed

    ### Confidence Intervals

    - Shows uncertainty in predictions
    - 95% confidence: We expect actual values to fall within this range 95% of the time
    - Wider intervals = more uncertainty

    ### Model Selection

    - **AIC/BIC:** Lower values indicate better fit
    - Start with simple models (low p, d, q values)
    - Increase complexity if needed
    - Consider seasonal patterns in energy data

    ### Typical Settings for Energy

    - **Daily data:** s=7 (weekly seasonality)
    - **Hourly data:** s=24 (daily seasonality)
    - **Monthly data:** s=12 (yearly seasonality)

    For Norwegian energy data, consider:
    - Strong seasonal patterns (s=365 for yearly)
    - Weather influences (use exogenous variables)
    - Different patterns for production vs consumption
    """)


# Footer
st.markdown("---")
st.caption(f"Assessment 4 - IND320 | SARIMAX({p},{d},{q})×({P},{D},{Q},{s}) | Forecast: {forecast_days} days")
