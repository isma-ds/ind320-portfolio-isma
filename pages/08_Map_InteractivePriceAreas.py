# pages/08_Map_InteractivePriceAreas.py
"""
Interactive Map with Norwegian Price Areas (NO1-NO5)
Assessment 4 - New Feature

Features:
- Display Norway map with price area boundaries
- Click to select coordinates (stored in session state)
- Choropleth coloring based on production/consumption data
- Time range selector
- Data type selector (production/consumption)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
from datetime import datetime, timedelta
import sys
sys.path.append('..')
from lib.mongodb_client import (
    get_aggregated_by_area_timerange,
    get_production_groups,
    get_consumption_groups
)

st.set_page_config(page_title="Interactive Price Area Map", page_icon="🗺️", layout="wide")

# ============================================================================
# TITLE AND DESCRIPTION
# ============================================================================

st.title("🗺️ Interactive Price Area Map")
st.markdown("""
This page displays Norwegian electricity price areas (NO1-NO5) on an interactive map.
Click on the map to select a location, choose a data type and time range to see
production or consumption patterns across different regions.
""")

# ============================================================================
# LOAD GEOJSON DATA
# ============================================================================

@st.cache_data
def load_geojson():
    """Load Norwegian price areas GeoJSON"""
    try:
        with open('geojson_data/elspot_areas.geojson', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("GeoJSON file not found. Please ensure geojson_data/elspot_areas.geojson exists.")
        return None
    except Exception as e:
        st.error(f"Error loading GeoJSON: {e}")
        return None

geojson_data = load_geojson()

if geojson_data is None:
    st.stop()

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'selected_coords' not in st.session_state:
    st.session_state.selected_coords = None

if 'selected_price_area' not in st.session_state:
    st.session_state.selected_price_area = None

# ============================================================================
# SIDEBAR CONTROLS
# ============================================================================

st.sidebar.header("Map Controls")

# Data type selector
data_type = st.sidebar.radio(
    "Data Type",
    options=["Production", "Consumption"],
    help="Select whether to display production or consumption data"
)

# Group selector based on data type
if data_type == "Production":
    available_groups = get_production_groups()
    group_label = "Production Group"
else:
    available_groups = get_consumption_groups()
    group_label = "Consumption Group"

if available_groups:
    selected_group = st.sidebar.selectbox(
        group_label,
        options=["All"] + available_groups,
        help="Select a specific group or 'All' for total"
    )
else:
    st.sidebar.warning(f"No {data_type.lower()} groups available")
    selected_group = "All"

# Time range selector
st.sidebar.subheader("Time Range")

col1, col2 = st.sidebar.columns(2)

with col1:
    start_date = st.date_input(
        "Start Date",
        value=datetime(2021, 1, 1),
        min_value=datetime(2021, 1, 1),
        max_value=datetime(2024, 12, 31)
    )

with col2:
    end_date = st.date_input(
        "End Date",
        value=datetime(2021, 1, 31),
        min_value=datetime(2021, 1, 1),
        max_value=datetime(2024, 12, 31)
    )

# Validate date range
if start_date > end_date:
    st.sidebar.error("Start date must be before end date!")
    st.stop()

# Calculate time range in days
time_range_days = (end_date - start_date).days
st.sidebar.info(f"Time range: {time_range_days} days")

# ============================================================================
# LOAD AGGREGATED DATA
# ============================================================================

@st.cache_data(ttl=600)
def get_map_data(data_type, start_date, end_date, group):
    """Get aggregated data for map visualization"""
    group_filter = None if group == "All" else group

    return get_aggregated_by_area_timerange(
        data_type=data_type.lower(),
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        group_column=group_filter
    )

with st.spinner("Loading data from MongoDB..."):
    aggregated_data = get_map_data(data_type, start_date, end_date, selected_group)

# ============================================================================
# CREATE CHOROPLETH MAP
# ============================================================================

def create_map(geojson, data_df):
    """Create interactive choropleth map"""

    # Create mapping from price area to mean quantity
    area_values = {}
    if not data_df.empty:
        for _, row in data_df.iterrows():
            area_values[row['priceArea']] = row['mean_quantity']

    # Extract coordinates and values for each feature
    lats = []
    lons = []
    values = []
    hover_texts = []

    for feature in geojson['features']:
        area = feature['properties']['omrade']
        name = feature['properties']['name']

        # Get center of polygon for marker
        coords = feature['geometry']['coordinates'][0]
        center_lon = sum(c[0] for c in coords) / len(coords)
        center_lat = sum(c[1] for c in coords) / len(coords)

        lons.append(center_lon)
        lats.append(center_lat)

        # Get value for this area
        value = area_values.get(area, 0)
        values.append(value)

        # Create hover text
        hover_text = f"<b>{area}</b><br>{name}<br>"
        if value > 0:
            unit = "MWh" if value > 1000 else "kWh"
            display_value = value / 1000 if value > 1000 else value
            hover_text += f"Mean: {display_value:,.1f} {unit}"
        else:
            hover_text += "No data"
        hover_texts.append(hover_text)

    # Create figure
    fig = go.Figure()

    # Add choropleth trace
    if len(values) > 0 and max(values) > 0:
        # Normalize values for color scale
        max_val = max(values)

        fig.add_trace(go.Scattergeo(
            lon=lons,
            lat=lats,
            text=hover_texts,
            mode='markers',
            marker=dict(
                size=40,
                color=values,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(
                    title=f"Mean<br>{data_type}<br>(kWh)",
                    x=1.02
                ),
                line=dict(width=1, color='white')
            ),
            hovertemplate='%{text}<extra></extra>',
            name=data_type
        ))

    # Add GeoJSON boundaries
    for feature in geojson['features']:
        coords = feature['geometry']['coordinates'][0]

        # Close the polygon
        lons_poly = [c[0] for c in coords] + [coords[0][0]]
        lats_poly = [c[1] for c in coords] + [coords[0][1]]

        area = feature['properties']['omrade']
        is_selected = (st.session_state.selected_price_area == area)

        fig.add_trace(go.Scattergeo(
            lon=lons_poly,
            lat=lats_poly,
            mode='lines',
            line=dict(
                width=3 if is_selected else 1,
                color='red' if is_selected else 'gray'
            ),
            name=area,
            showlegend=False,
            hoverinfo='skip'
        ))

    # Add selected coordinate marker
    if st.session_state.selected_coords:
        lat, lon = st.session_state.selected_coords
        fig.add_trace(go.Scattergeo(
            lon=[lon],
            lat=[lat],
            mode='markers',
            marker=dict(
                size=15,
                color='red',
                symbol='star',
                line=dict(width=2, color='white')
            ),
            name='Selected Point',
            hovertemplate=f'<b>Selected Location</b><br>Lat: {lat:.4f}<br>Lon: {lon:.4f}<extra></extra>'
        ))

    # Update layout
    fig.update_geos(
        scope='europe',
        center=dict(lat=65, lon=13),
        projection_scale=4,
        showland=True,
        landcolor='rgb(243, 243, 243)',
        coastlinecolor='rgb(204, 204, 204)',
        showcountries=True,
        countrycolor='rgb(204, 204, 204)',
        showlakes=True,
        lakecolor='rgb(200, 230, 255)'
    )

    fig.update_layout(
        title=f"{data_type} Distribution - {selected_group} ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})",
        height=700,
        margin=dict(l=0, r=0, t=50, b=0)
    )

    return fig

# ============================================================================
# DISPLAY MAP
# ============================================================================

st.subheader("Norwegian Price Areas Map")

fig = create_map(geojson_data, aggregated_data)

# Note: Plotly's click events in Streamlit are limited
# We'll add a manual coordinate input as alternative

st.plotly_chart(fig, use_container_width=True, key="main_map")

# ============================================================================
# COORDINATE SELECTION (Manual Input Alternative)
# ============================================================================

st.subheader("Select Location")

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    selected_lat = st.number_input(
        "Latitude",
        min_value=58.0,
        max_value=71.0,
        value=60.39 if st.session_state.selected_coords is None else st.session_state.selected_coords[0],
        step=0.01,
        help="Latitude in decimal degrees (58°N to 71°N covers Norway)"
    )

with col2:
    selected_lon = st.number_input(
        "Longitude",
        min_value=4.0,
        max_value=31.0,
        value=5.32 if st.session_state.selected_coords is None else st.session_state.selected_coords[1],
        step=0.01,
        help="Longitude in decimal degrees (4°E to 31°E covers Norway)"
    )

with col3:
    st.write("")  # Spacing
    st.write("")  # Spacing
    if st.button("📍 Set Location", use_container_width=True):
        st.session_state.selected_coords = (selected_lat, selected_lon)

        # Determine which price area this coordinate falls in
        # Simple point-in-polygon check (simplified)
        for feature in geojson_data['features']:
            # For simplicity, just check if within bounding box
            coords = feature['geometry']['coordinates'][0]
            lons = [c[0] for c in coords]
            lats = [c[1] for c in coords]

            if (min(lons) <= selected_lon <= max(lons) and
                min(lats) <= selected_lat <= max(lats)):
                st.session_state.selected_price_area = feature['properties']['omrade']
                break

        st.rerun()

# Display selected information
if st.session_state.selected_coords:
    st.success(f"✅ Location set: {st.session_state.selected_coords[0]:.4f}°N, {st.session_state.selected_coords[1]:.4f}°E")
    if st.session_state.selected_price_area:
        st.info(f"📍 This location is in price area: **{st.session_state.selected_price_area}**")

# ============================================================================
# DATA SUMMARY
# ============================================================================

st.subheader("Data Summary")

if not aggregated_data.empty:
    col1, col2, col3 = st.columns(3)

    with col1:
        total = aggregated_data['total_quantity'].sum()
        st.metric(
            "Total Quantity",
            f"{total/1000:,.0f} MWh"
        )

    with col2:
        mean = aggregated_data['mean_quantity'].mean()
        st.metric(
            "Average per Area",
            f"{mean/1000:,.1f} MWh"
        )

    with col3:
        max_area = aggregated_data.loc[aggregated_data['mean_quantity'].idxmax(), 'priceArea']
        st.metric(
            "Highest Area",
            max_area
        )

    # Show data table
    with st.expander("📊 View Detailed Data by Price Area"):
        display_df = aggregated_data.copy()
        display_df['mean_quantity'] = display_df['mean_quantity'] / 1000  # Convert to MWh
        display_df['total_quantity'] = display_df['total_quantity'] / 1000
        display_df.columns = ['Price Area', 'Mean (MWh)', 'Total (MWh)']
        st.dataframe(
            display_df.style.format({
                'Mean (MWh)': '{:.1f}',
                'Total (MWh)': '{:.0f}'
            }),
            use_container_width=True
        )
else:
    st.warning("No data available for the selected time range and filters.")

# ============================================================================
# INSTRUCTIONS
# ============================================================================

with st.expander("ℹ️ How to Use This Page"):
    st.markdown("""
    ### Map Features

    1. **View Price Areas**: The map shows all 5 Norwegian electricity price areas (NO1-NO5)
    2. **Select Data Type**: Choose between Production and Consumption data
    3. **Filter by Group**: Select a specific production/consumption group or view all
    4. **Set Time Range**: Choose start and end dates to analyze
    5. **Color Coding**: Areas are colored based on mean values (darker = higher)

    ### Select a Location

    - **Manual Input**: Enter latitude and longitude coordinates
    - **Click Set Location**: Store the coordinates for use in other analyses
    - The selected location will be marked with a ⭐ on the map
    - The system will identify which price area the location falls within

    ### Using Selected Coordinates

    The coordinates you select here will be stored and can be used by other pages:
    - **Snow Drift Analysis**: Requires coordinates to fetch weather data
    - **Weather Analysis**: Uses coordinates for location-specific data

    ### Data Source

    - Production/Consumption data from MongoDB (Elhub 2021-2024)
    - Aggregated by price area over the selected time range
    - Real-time calculations based on your selections
    """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("🗺️ Assessment 4 - Interactive Price Area Map | Data: Elhub via MongoDB Atlas")
