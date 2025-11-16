"""
Assessment 4 - Energy Production/Consumption Choropleth Visualization
Color price areas by mean energy values over selected time intervals
"""

import streamlit as st
import plotly.graph_objects as go
import json
import pandas as pd
from datetime import datetime, timedelta
from pymongo import MongoClient

st.set_page_config(page_title="Energy Choropleth", page_icon="🌡️", layout="wide")

st.title("🌡️ Energy Production/Consumption Choropleth")

st.markdown("""
Visualize energy production or consumption across Norwegian price areas.
Areas are colored based on mean values over your selected time interval.
""")


# MongoDB connection function
@st.cache_resource
def get_mongo_client():
    """Connect to MongoDB"""
    mongo_uri = st.secrets.get("MONGO_URI", "mongodb+srv://ismasohail_user:IsmaMinhas@cluster0.e3wct64.mongodb.net/ind320?retryWrites=true&w=majority&appName=Cluster0")
    return MongoClient(mongo_uri)


# Load GeoJSON
@st.cache_data
def load_price_areas_geojson():
    """Load Norwegian price area boundaries"""
    with open('geojson_data/elspot_areas.geojson', 'r', encoding='utf-8')  as f:
        return json.load(f)


# Fetch energy data from MongoDB
@st.cache_data(ttl=3600)
def fetch_energy_data(collection_name, start_date, end_date, metric_type):
    """Fetch energy data from MongoDB for the selected period"""
    try:
        client = get_mongo_client()
        db = client["ind320"]
        collection = db[collection_name]

        # Query MongoDB for data in date range
        query = {
            "startTime": {
                "$gte": start_date,
                "$lte": end_date
            }
        }

        data = list(collection.find(query))

        if not data:
            return None

        df = pd.DataFrame(data)

        # Clean up column names
        if metric_type == "production":
            df = df.rename(columns={"productionGroup": "group", "quantityMWh": "value"})
        else:
            df = df.rename(columns={"consumptionGroup": "group", "quantityMWh": "value"})

        return df

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None


# Sidebar controls
st.sidebar.header("Visualization Controls")

# Select production or consumption
metric_type = st.sidebar.radio(
    "Select Metric Type:",
    options=["Production", "Consumption"],
    index=0
)

# Time period selection
st.sidebar.subheader("Time Period")

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
        value=datetime(2021, 1, 31),
        min_value=datetime(2021, 1, 1),
        max_value=datetime(2024, 12, 31)
    )

# Convert to datetime
start_datetime = datetime.combine(start_date, datetime.min.time())
end_datetime = datetime.combine(end_date, datetime.max.time())

# Calculate days in range
days_in_range = (end_datetime - start_datetime).days + 1
st.sidebar.info(f"Selected period: {days_in_range} days")


# Group selection
if metric_type == "Production":
    available_groups = ["Hydro", "Wind", "Thermal", "Solar", "All"]
    collection_name = "elhub_production_2021" if start_date.year == 2021 else "elhub_production_2022_2024"
else:
    available_groups = ["Residential", "Commercial", "Industrial", "Other", "All"]
    collection_name = "elhub_consumption_2021" if start_date.year == 2021 else "elhub_consumption_2022_2024"

selected_group = st.sidebar.selectbox(
    f"Select {metric_type} Group:",
    options=available_groups,
    index=0
)


# Fetch and process data
with st.spinner(f"Fetching {metric_type.lower()} data..."):
    df = fetch_energy_data(collection_name, start_datetime, end_datetime, metric_type.lower())

if df is None or df.empty:
    st.warning(f"No {metric_type.lower()} data found for the selected period. Try a different date range.")
    st.stop()

# Filter by group if not "All"
if selected_group != "All":
    df = df[df['group'] == selected_group]

# Calculate mean values per price area
area_means = df.groupby('priceArea')['value'].mean().reset_index()
area_means.columns = ['priceArea', 'meanValue']

# Normalize price area names (remove spaces)
area_means['priceArea'] = area_means['priceArea'].str.replace(' ', '')

# Display statistics
st.subheader("Data Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Records", f"{len(df):,}")

with col2:
    st.metric("Mean Value", f"{df['value'].mean():.2f} MWh")

with col3:
    st.metric("Max Value", f"{df['value'].max():.2f} MWh")

with col4:
    st.metric("Min Value", f"{df['value'].min():.2f} MWh")


# Display mean values table
st.subheader("Mean Values by Price Area")

# Display table
display_df = area_means.copy()
display_df.columns = ['Price Area', 'Mean Value (MWh)']
display_df = display_df.sort_values('Price Area')

st.dataframe(display_df, use_container_width=True)


# Create choropleth map
st.subheader(f"{metric_type} Choropleth Map")

try:
    geojson = load_price_areas_geojson()

    # Create figure
    fig = go.Figure()

    # Get min and max for color scale
    min_val = area_means['meanValue'].min()
    max_val = area_means['meanValue'].max()

    # Add GeoJSON layers with colors based on values
    for feature in geojson['features']:
        area_name = feature['properties'].get('ElSpotOmr', 'Unknown').replace(' ', '')

        # Get mean value for this area
        area_data = area_means[area_means['priceArea'] == area_name]

        if area_data.empty:
            # No data for this area - use gray
            fill_color = 'rgba(128, 128, 128, 0.3)'
            mean_value = 0
        else:
            mean_value = area_data['meanValue'].values[0]

            # Calculate color based on value (blue to red scale)
            if max_val > min_val:
                normalized = (mean_value - min_val) / (max_val - min_val)
            else:
                normalized = 0.5

            # Create color (blue=low, red=high)
            r = int(255 * normalized)
            g = int(255 * (1 - abs(2 * normalized - 1)))  # Green peaks at middle
            b = int(255 * (1 - normalized))

            fill_color = f'rgba({r}, {g}, {b}, 0.6)'

        # Extract coordinates
        if feature['geometry']['type'] == 'Polygon':
            coords_list = [feature['geometry']['coordinates']]
        elif feature['geometry']['type'] == 'MultiPolygon':
            coords_list = feature['geometry']['coordinates']
        else:
            continue

        # Add polygons
        for coords in coords_list:
            for polygon in coords:
                lons = [coord[0] for coord in polygon]
                lats = [coord[1] for coord in polygon]

                fig.add_trace(go.Scattermapbox(
                    lon=lons,
                    lat=lats,
                    mode='lines',
                    fill='toself',
                    fillcolor=fill_color,
                    line=dict(width=1.5, color='white'),
                    opacity=0.8,
                    name=f"{area_name}: {mean_value:.2f} MWh",
                    text=f"{area_name}<br>Mean: {mean_value:.2f} MWh",
                    hoverinfo='text',
                    showlegend=True
                ))

    # Configure layout
    fig.update_layout(
        mapbox=dict(
            style='open-street-map',
            center=dict(lat=65.0, lon=12.0),
            zoom=4
        ),
        height=600,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255, 255, 255, 0.9)"
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # Color scale legend
    st.markdown("""
    **Color Scale:**
    - 🔵 Blue = Low values
    - 🟢 Green = Medium values
    - 🔴 Red = High values
    """)

except Exception as e:
    st.error(f"Error creating choropleth map: {e}")


# Time series plot for selected areas
st.subheader("Time Series Comparison")

selected_areas_for_plot = st.multiselect(
    "Select price areas to compare:",
    options=sorted(df['priceArea'].unique()),
    default=sorted(df['priceArea'].unique())[:2] if len(df['priceArea'].unique()) >= 2 else sorted(df['priceArea'].unique())
)

if selected_areas_for_plot:
    # Filter data
    plot_df = df[df['priceArea'].isin(selected_areas_for_plot)].copy()

    # Aggregate by date and area
    plot_df['date'] = pd.to_datetime(plot_df['startTime']).dt.date
    daily_data = plot_df.groupby(['date', 'priceArea'])['value'].mean().reset_index()

    # Create line plot
    fig_ts = go.Figure()

    for area in selected_areas_for_plot:
        area_data = daily_data[daily_data['priceArea'] == area]

        fig_ts.add_trace(go.Scatter(
            x=area_data['date'],
            y=area_data['value'],
            mode='lines',
            name=area,
            line=dict(width=2)
        ))

    fig_ts.update_layout(
        title=f"Daily Average {metric_type} - {selected_group}",
        xaxis_title="Date",
        yaxis_title=f"{metric_type} (MWh)",
        height=400,
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    st.plotly_chart(fig_ts, use_container_width=True)


# Information
with st.expander("ℹ️ How to Interpret This Visualization"):
    st.markdown(f"""
    This choropleth map shows the mean {metric_type.lower()} values across Norwegian price areas
    for the selected time period.

    **Key Points:**
    - Each price area is colored based on its mean {metric_type.lower()} value
    - Darker/redder colors indicate higher values
    - Lighter/bluer colors indicate lower values
    - Gray areas have no data for the selected period

    **Use Cases:**
    - Identify regions with high/low {metric_type.lower()}
    - Compare {metric_type.lower()} patterns across areas
    - Analyze temporal changes by adjusting the date range
    - Understand regional energy dynamics
    """)


# Footer
st.markdown("---")
st.caption(f"Assessment 4 - IND320 | Showing {metric_type} data from {start_date} to {end_date}")
