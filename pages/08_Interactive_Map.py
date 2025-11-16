"""
Assessment 4 - Interactive Map with Norwegian Price Areas
Allows users to click coordinates and select price areas for analysis
"""

import streamlit as st
import plotly.graph_objects as go
import json
import pandas as pd

st.set_page_config(page_title="Interactive Map", page_icon="🗺️", layout="wide")

st.title("🗺️ Interactive Map - Norwegian Electricity Price Areas")

st.markdown("""
Select a location on the map to analyze energy data and meteorological patterns.
The map shows Norwegian electricity price areas (NO1-NO5).
""")

# Load GeoJSON data for Norwegian price areas
@st.cache_data
def load_price_areas_geojson():
    """Load Norwegian price area boundaries from GeoJSON"""
    with open('geojson_data/elspot_areas.geojson', 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
    return geojson_data


# Initialize session state for clicked coordinates and selected area
if 'clicked_lat' not in st.session_state:
    st.session_state.clicked_lat = None
if 'clicked_lon' not in st.session_state:
    st.session_state.clicked_lon = None
if 'selected_price_area' not in st.session_state:
    st.session_state.selected_price_area = None


# Load GeoJSON
try:
    geojson = load_price_areas_geojson()

    # Extract price area names
    price_areas = []
    for feature in geojson['features']:
        area_name = feature['properties'].get('ElSpotOmr', 'Unknown')
        price_areas.append(area_name)

    st.success(f"Loaded {len(geojson['features'])} price areas: {', '.join(sorted(price_areas))}")

except Exception as e:
    st.error(f"Error loading GeoJSON data: {e}")
    st.stop()


# Sidebar controls
st.sidebar.header("Map Controls")

# Price area selector
selected_area = st.sidebar.selectbox(
    "Select Price Area:",
    options=["None"] + sorted(list(set(price_areas))),
    index=0
)

if selected_area != "None":
    st.session_state.selected_price_area = selected_area


# Display map with GeoJSON overlays
st.subheader("Norwegian Price Areas Map")

# Create figure
fig = go.Figure()

# Add GeoJSON layers for each price area
for feature in geojson['features']:
    area_name = feature['properties'].get('ElSpotOmr', 'Unknown')

    # Determine if this area is selected
    is_selected = (area_name == st.session_state.selected_price_area)

    # Extract coordinates from GeoJSON geometry
    if feature['geometry']['type'] == 'Polygon':
        coords_list = [feature['geometry']['coordinates']]
    elif feature['geometry']['type'] == 'MultiPolygon':
        coords_list = feature['geometry']['coordinates']
    else:
        continue

    # Add each polygon
    for coords in coords_list:
        for polygon in coords:
            # Convert to lat/lon (GeoJSON is lon/lat)
            lons = [coord[0] for coord in polygon]
            lats = [coord[1] for coord in polygon]

            # Style based on selection
            if is_selected:
                line_color = 'red'
                line_width = 3
                fill_color = 'rgba(255, 0, 0, 0.2)'
                opacity = 0.6
            else:
                line_color = 'blue'
                line_width = 1.5
                fill_color = 'rgba(0, 0, 255, 0.05)'
                opacity = 0.3

            # Add polygon trace
            fig.add_trace(go.Scattermapbox(
                lon=lons,
                lat=lats,
                mode='lines',
                fill='toself',
                fillcolor=fill_color,
                line=dict(width=line_width, color=line_color),
                opacity=opacity,
                name=area_name,
                text=area_name,
                hoverinfo='text',
                showlegend=False
            ))

# Add clicked point marker if exists
if st.session_state.clicked_lat is not None and st.session_state.clicked_lon is not None:
    fig.add_trace(go.Scattermapbox(
        lon=[st.session_state.clicked_lon],
        lat=[st.session_state.clicked_lat],
        mode='markers',
        marker=dict(size=15, color='green', symbol='circle'),
        name='Selected Location',
        text=f'Selected: ({st.session_state.clicked_lat:.4f}, {st.session_state.clicked_lon:.4f})',
        hoverinfo='text',
        showlegend=True
    ))

# Configure map layout
fig.update_layout(
    mapbox=dict(
        style='open-street-map',
        center=dict(lat=65.0, lon=12.0),  # Center of Norway
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
        bgcolor="rgba(255, 255, 255, 0.8)"
    )
)

# Display map
st.plotly_chart(fig, use_container_width=True)

# Instructions and coordinate input
st.subheader("Set Location Coordinates")

col1, col2 = st.columns(2)

with col1:
    input_lat = st.number_input(
        "Latitude:",
        min_value=58.0,
        max_value=71.0,
        value=60.0 if st.session_state.clicked_lat is None else st.session_state.clicked_lat,
        step=0.01,
        format="%.4f"
    )

with col2:
    input_lon = st.number_input(
        "Longitude:",
        min_value=4.0,
        max_value=31.0,
        value=10.0 if st.session_state.clicked_lon is None else st.session_state.clicked_lon,
        step=0.01,
        format="%.4f"
    )

if st.button("Set Coordinates"):
    st.session_state.clicked_lat = input_lat
    st.session_state.clicked_lon = input_lon
    st.success(f"Coordinates set to: ({input_lat:.4f}, {input_lon:.4f})")
    st.rerun()


# Display current selection
st.subheader("Current Selection")

if st.session_state.clicked_lat is not None and st.session_state.clicked_lon is not None:
    st.info(f"""
    **Selected Location:**
    - Latitude: {st.session_state.clicked_lat:.4f}
    - Longitude: {st.session_state.clicked_lon:.4f}

    **Selected Price Area:** {st.session_state.selected_price_area or "None"}

    These coordinates will be used for:
    - Snow drift calculations
    - Meteorological data fetching
    - Location-specific energy analysis
    """)
else:
    st.warning("No location selected yet. Enter coordinates above and click 'Set Coordinates'.")


# Quick location presets
st.subheader("Quick Location Presets")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Oslo (NO1)"):
        st.session_state.clicked_lat = 59.9139
        st.session_state.clicked_lon = 10.7522
        st.session_state.selected_price_area = "NO 1"
        st.rerun()

with col2:
    if st.button("Bergen (NO5)"):
        st.session_state.clicked_lat = 60.3929
        st.session_state.clicked_lon = 5.3241
        st.session_state.selected_price_area = "NO 5"
        st.rerun()

with col3:
    if st.button("Trondheim (NO3)"):
        st.session_state.clicked_lat = 63.4305
        st.session_state.clicked_lon = 10.3951
        st.session_state.selected_price_area = "NO 3"
        st.rerun()


# Information section
with st.expander("ℹ️ About Norwegian Price Areas"):
    st.markdown("""
    Norway is divided into 5 electricity price areas (bidding zones):

    - **NO1 - Eastern Norway (Oslo):** Highest population density, major consumption center
    - **NO2 - Southern Norway (Kristiansand):** Industrial areas, interconnectors to Europe
    - **NO3 - Central Norway (Trondheim):** Balanced production and consumption
    - **NO4 - Northern Norway (Tromsø):** Surplus production, industrial consumers
    - **NO5 - Western Norway (Bergen):** High hydropower production

    Price areas help manage electricity flow and pricing based on regional supply and demand.
    """)


# Footer
st.markdown("---")
st.caption("Assessment 4 - IND320 | Data: NVE (Norwegian Water Resources and Energy Directorate)")
