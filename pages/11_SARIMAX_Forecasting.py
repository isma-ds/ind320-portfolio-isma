# pages/11_SARIMAX_Forecasting.py
"""
SARIMAX Forecasting for Energy Production and Consumption
Assessment 4 - New Feature

Interactive interface for SARIMAX time series forecasting with:
- Configurable SARIMAX parameters (p,d,q)(P,D,Q,s)
- Selectable exogenous variables
- Dynamic forecasting with confidence intervals
- Training/test split visualization
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

import sys
sys.path.append('..')
from lib.mongodb_client import load_production_all_years, load_consumption_all_years

st.set_page_config(page_title="SARIMAX Forecasting", page_icon="📈", layout="wide")

# ============================================================================
# TITLE AND DESCRIPTION
# ============================================================================

st.title("📈 SARIMAX Forecasting - Energy Production & Consumption")
st.markdown("""
This page provides an interactive interface for forecasting energy production or consumption
using SARIMAX (Seasonal AutoRegressive Integrated Moving Average with eXogenous factors).

Configure all model parameters and visualize forecasts with confidence intervals.
""")

# ============================================================================
# SIDEBAR CONTROLS - DATA SELECTION
# ============================================================================

st.sidebar.header("Data Selection")

# Data type
data_type = st.sidebar.radio(
    "Data Type",
    options=["Production", "Consumption"]
)

# Price area
price_area = st.sidebar.selectbox(
    "Price Area",
    options=['NO1', 'NO2', 'NO3', 'NO4', 'NO5']
)

# Group selection
if data_type == "Production":
    from lib.mongodb_client import get_production_groups
    groups = get_production_groups()
    selected_group = st.sidebar.selectbox("Production Group", groups if groups else ['Hydro', 'Wind'])
else:
    selected_group = "Total"
    st.sidebar.info("Consumption: Using total consumption")

# Time range for training
st.sidebar.subheader("Training Data Range")

col1, col2 = st.sidebar.columns(2)
with col1:
    train_start = st.date_input(
        "Start Date",
        value=datetime(2021, 1, 1),
        min_value=datetime(2021, 1, 1),
        max_value=datetime(2024, 6, 30)
    )

with col2:
    train_end = st.date_input(
        "End Date",
        value=datetime(2022, 12, 31),
        min_value=datetime(2021, 1, 1),
        max_value=datetime(2024, 11, 30)
    )

if train_start >= train_end:
    st.sidebar.error("End date must be after start date")
    st.stop()

# Forecast horizon
forecast_days = st.sidebar.slider(
    "Forecast Horizon (days)",
    min_value=7,
    max_value=90,
    value=30,
    step=7
)

# ============================================================================
# SIDEBAR CONTROLS - SARIMAX PARAMETERS
# ============================================================================

st.sidebar.subheader("SARIMAX Parameters")

st.sidebar.markdown("**Non-seasonal components (p,d,q)**")
col1, col2, col3 = st.sidebar.columns(3)
with col1:
    p = st.number_input("p (AR)", min_value=0, max_value=5, value=1, step=1,
                        help="Autoregressive order")
with col2:
    d = st.number_input("d (I)", min_value=0, max_value=2, value=1, step=1,
                        help="Differencing order")
with col3:
    q = st.number_input("q (MA)", min_value=0, max_value=5, value=1, step=1,
                        help="Moving average order")

st.sidebar.markdown("**Seasonal components (P,D,Q,s)**")
col1, col2, col3, col4 = st.sidebar.columns(4)
with col1:
    P = st.number_input("P", min_value=0, max_value=3, value=1, step=1,
                        help="Seasonal AR order")
with col2:
    D = st.number_input("D", min_value=0, max_value=2, value=1, step=1,
                        help="Seasonal differencing")
with col3:
    Q = st.number_input("Q", min_value=0, max_value=3, value=1, step=1,
                        help="Seasonal MA order")
with col4:
    s = st.number_input("s", min_value=0, max_value=168, value=24, step=1,
                        help="Seasonal period (24=daily, 168=weekly)")

# Exogenous variables (placeholder - simplified for now)
st.sidebar.subheader("Exogenous Variables")
use_exog = st.sidebar.checkbox(
    "Include time features",
    value=False,
    help="Add hour, day of week, month as exogenous variables"
)

# ============================================================================
# LOAD AND PREPARE DATA
# ============================================================================

st.subheader("Loading Data...")

@st.cache_data(ttl=600)
def load_energy_data(data_type, price_area, group, start_date, end_date):
    """Load and aggregate energy data"""
    if data_type == "Production":
        df = load_production_all_years()
        group_col = 'productionGroup'
    else:
        df = load_consumption_all_years()
        group_col = 'consumptionGroup'

    if df.empty:
        return None

    # Filter
    df = df[df['priceArea'] == price_area]

    if data_type == "Production":
        df = df[df[group_col] == group]

    df = df[
        (df['startTime'] >= pd.Timestamp(start_date)) &
        (df['startTime'] <= pd.Timestamp(end_date))
    ]

    if df.empty:
        return None

    # Aggregate to hourly
    qty_col = 'quantityKwh' if 'quantityKwh' in df.columns else 'quantityMWh'
    hourly = df.groupby('startTime')[qty_col].sum().reset_index()
    hourly.columns = ['time', 'quantity']
    hourly = hourly.set_index('time').sort_index()

    return hourly

with st.spinner("Loading data from MongoDB..."):
    energy_data = load_energy_data(
        data_type,
        price_area,
        selected_group,
        train_start,
        train_end
    )

if energy_data is None or energy_data.empty:
    st.error(f"No data available for {price_area} - {selected_group} in the selected range")
    st.stop()

st.success(f"✅ Loaded {len(energy_data):,} hours of data")

# Prepare time series
ts = energy_data['quantity']

# Add exogenous variables if requested
exog_train = None
exog_forecast = None

if use_exog:
    exog_train = pd.DataFrame({
        'hour': ts.index.hour,
        'dayofweek': ts.index.dayofweek,
        'month': ts.index.month
    }, index=ts.index)

    # Create future exogenous variables
    forecast_start = ts.index[-1] + pd.Timedelta(hours=1)
    forecast_index = pd.date_range(
        start=forecast_start,
        periods=forecast_days * 24,
        freq='H'
    )

    exog_forecast = pd.DataFrame({
        'hour': forecast_index.hour,
        'dayofweek': forecast_index.dayofweek,
        'month': forecast_index.month
    }, index=forecast_index)

# ============================================================================
# FIT SARIMAX MODEL
# ============================================================================

st.subheader("Training SARIMAX Model...")

try:
    with st.spinner("Fitting SARIMAX model... This may take a minute."):
        # Fit model
        model = SARIMAX(
            ts,
            order=(p, d, q),
            seasonal_order=(P, D, Q, s),
            exog=exog_train,
            enforce_stationarity=False,
            enforce_invertibility=False
        )

        results = model.fit(disp=False, maxiter=200)

    st.success("✅ Model fitted successfully!")

    # Display model summary
    with st.expander("📊 Model Summary"):
        st.text(str(results.summary()))

except Exception as e:
    st.error(f"Error fitting model: {e}")
    st.info("Try adjusting the parameters or reducing the model complexity.")
    st.stop()

# ============================================================================
# GENERATE FORECAST
# ============================================================================

st.subheader("Generating Forecast...")

try:
    # Forecast
    forecast_result = results.get_forecast(
        steps=forecast_days * 24,
        exog=exog_forecast
    )

    forecast_mean = forecast_result.predicted_mean
    forecast_ci = forecast_result.conf_int(alpha=0.05)  # 95% confidence interval

    st.success(f"✅ Generated {forecast_days}-day forecast")

except Exception as e:
    st.error(f"Error generating forecast: {e}")
    st.stop()

# ============================================================================
# VISUALIZATION
# ============================================================================

st.subheader("Forecast Visualization")

# Create figure
fig = go.Figure()

# Historical data
fig.add_trace(go.Scatter(
    x=ts.index,
    y=ts.values,
    mode='lines',
    name='Historical Data',
    line=dict(color='blue', width=1)
))

# Forecast
fig.add_trace(go.Scatter(
    x=forecast_mean.index,
    y=forecast_mean.values,
    mode='lines',
    name='Forecast',
    line=dict(color='red', width=2)
))

# Confidence interval
fig.add_trace(go.Scatter(
    x=forecast_ci.index.tolist() + forecast_ci.index.tolist()[::-1],
    y=forecast_ci.iloc[:, 1].tolist() + forecast_ci.iloc[:, 0].tolist()[::-1],
    fill='toself',
    fillcolor='rgba(255,0,0,0.2)',
    line=dict(color='rgba(255,255,255,0)'),
    name='95% Confidence Interval',
    showlegend=True
))

fig.update_layout(
    title=f"{data_type} Forecast: {price_area} - {selected_group}",
    xaxis_title="Time",
    yaxis_title="Quantity (kWh/MWh)",
    hovermode='x unified',
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# FORECAST STATISTICS
# ============================================================================

st.subheader("📊 Forecast Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Mean Forecast",
        f"{forecast_mean.mean():,.0f}"
    )

with col2:
    st.metric(
        "Forecast Range",
        f"{forecast_mean.max() - forecast_mean.min():,.0f}"
    )

with col3:
    st.metric(
        "Avg CI Width",
        f"{(forecast_ci.iloc[:, 1] - forecast_ci.iloc[:, 0]).mean():,.0f}"
    )

with col4:
    last_historical = ts.iloc[-1]
    first_forecast = forecast_mean.iloc[0]
    change = ((first_forecast - last_historical) / last_historical) * 100
    st.metric(
        "Initial Change",
        f"{change:+.1f}%"
    )

# Model diagnostics
with st.expander("🔍 Model Diagnostics"):
    col1, col2 = st.columns(2)

    with col1:
        st.metric("AIC", f"{results.aic:.1f}", help="Akaike Information Criterion (lower is better)")
        st.metric("BIC", f"{results.bic:.1f}", help="Bayesian Information Criterion (lower is better)")

    with col2:
        st.metric("Log-Likelihood", f"{results.llf:.1f}")
        st.metric("Number of Observations", f"{results.nobs:,.0f}")

    st.markdown("""
    **Interpretation**:
    - **AIC/BIC**: Lower values indicate better model fit (penalized for complexity)
    - **Log-Likelihood**: Higher is better (measures fit quality)
    - Confidence interval width increases with forecast horizon (normal behavior)
    """)

# ============================================================================
# RESIDUALS ANALYSIS
# ============================================================================

with st.expander("📉 Residuals Analysis"):
    residuals = results.resid

    fig_resid = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Residuals Over Time", "Residuals Distribution")
    )

    # Residuals time series
    fig_resid.add_trace(
        go.Scatter(x=residuals.index, y=residuals.values, mode='lines', name='Residuals'),
        row=1, col=1
    )

    # Residuals histogram
    fig_resid.add_trace(
        go.Histogram(x=residuals.values, name='Distribution', nbinsx=50),
        row=2, col=1
    )

    fig_resid.update_xaxes(title_text="Time", row=1, col=1)
    fig_resid.update_xaxes(title_text="Residual Value", row=2, col=1)
    fig_resid.update_yaxes(title_text="Residual", row=1, col=1)
    fig_resid.update_yaxes(title_text="Count", row=2, col=1)

    fig_resid.update_layout(height=600, showlegend=False)

    st.plotly_chart(fig_resid, use_container_width=True)

    st.markdown("""
    **Good residuals should**:
    - Have mean close to zero
    - Be randomly distributed (no patterns)
    - Follow approximately normal distribution
    """)

# ============================================================================
# EXPORT FORECAST
# ============================================================================

with st.expander("💾 Export Forecast Data"):
    forecast_df = pd.DataFrame({
        'time': forecast_mean.index,
        'forecast': forecast_mean.values,
        'lower_95': forecast_ci.iloc[:, 0].values,
        'upper_95': forecast_ci.iloc[:, 1].values
    })

    forecast_df['data_type'] = data_type
    forecast_df['price_area'] = price_area
    forecast_df['group'] = selected_group
    forecast_df['model'] = f"SARIMAX({p},{d},{q})({P},{D},{Q},{s})"

    csv = forecast_df.to_csv(index=False)

    st.download_button(
        label="📥 Download Forecast CSV",
        data=csv,
        file_name=f"forecast_{price_area}_{selected_group}_{forecast_days}days.csv",
        mime="text/csv"
    )

# ============================================================================
# METHODOLOGY
# ============================================================================

with st.expander("ℹ️ SARIMAX Methodology"):
    st.markdown("""
    ### SARIMAX Model

    **SARIMAX** = Seasonal AutoRegressive Integrated Moving Average with eXogenous factors

    #### Model Components:

    **Non-seasonal: (p, d, q)**
    - **p**: Autoregressive order (how many past values to use)
    - **d**: Differencing order (make series stationary)
    - **q**: Moving average order (past forecast errors)

    **Seasonal: (P, D, Q, s)**
    - **P**: Seasonal autoregressive order
    - **D**: Seasonal differencing
    - **Q**: Seasonal moving average order
    - **s**: Seasonal period (24 hours for daily pattern, 168 for weekly)

    **Exogenous Variables** (Optional):
    - Additional predictors (time features, weather, etc.)
    - Can improve forecast accuracy

    #### How to Use:

    1. **Start Simple**: Try (1,1,1)(1,1,1,24) for hourly data with daily seasonality
    2. **Check Diagnostics**: Look at AIC/BIC - lower is better
    3. **Inspect Residuals**: Should be random with no patterns
    4. **Adjust Parameters**: Increase complexity if needed, but avoid overfitting

    #### Typical Patterns:

    - **Daily seasonality**: s=24 (hourly data)
    - **Weekly seasonality**: s=168 (hourly data)
    - **Monthly seasonality**: s=720 (hourly data, approximate)

    #### Data Source:
    - Historical data from MongoDB (Elhub 2021-2024)
    - Model trained on selected time range
    - Forecast generated for specified horizon

    #### Limitations:
    - Assumes patterns continue into future
    - Uncertainty increases with longer horizons
    - External shocks not predicted
    """)

# ============================================================================
# TIPS
# ============================================================================

with st.expander("💡 Parameter Selection Tips"):
    st.markdown("""
    ### Choosing Good Parameters

    **For Energy Production/Consumption:**

    **Hydro Production**:
    - Try: (1,1,1)(1,1,1,168) - weekly seasonality
    - Influenced by weather, seasonal patterns

    **Wind Production**:
    - Try: (2,1,1)(1,1,1,24) - daily patterns
    - High variability, harder to forecast

    **Consumption**:
    - Try: (1,1,1)(2,1,1,24) - strong daily cycle
    - Clear patterns (work hours, heating/cooling)

    **General Tips**:
    1. Start with low values (1,1,1)(1,1,1,s)
    2. If AIC/BIC doesn't improve, don't increase complexity
    3. Check residuals - they should look random
    4. Longer forecast horizons = wider confidence intervals
    5. Use exogenous variables carefully (need future values!)

    **Troubleshooting**:
    - Model won't fit: Reduce complexity or differencing
    - Poor forecast: Try different seasonal period (s)
    - Wide confidence intervals: Normal for long horizons
    - Weird patterns in residuals: Adjust (p,q) or seasonal components
    """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("📈 Assessment 4 - SARIMAX Forecasting | Data: Elhub via MongoDB Atlas")
