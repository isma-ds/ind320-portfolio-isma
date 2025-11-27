"""
MongoDB client for Streamlit pages - Assessment 2/3/4
Replaces all CSV downloads with MongoDB queries.

CRITICAL: This file ensures NO CSV downloads in Streamlit app.
All data must come from MongoDB to pass Assessment 2.

Assessment 4 additions:
- Support for 2022-2024 production data
- Support for 2021-2024 consumption data
- Time range filtering for forecasting and correlation analysis
"""

import streamlit as st
from pymongo import MongoClient
import pandas as pd
from typing import Optional, List

@st.cache_resource
def get_mongo_client():
    """
    Get cached MongoDB client.

    Returns:
        MongoClient or None: MongoDB client instance
    """
    try:
        mongo_uri = st.secrets["MONGO_URI"]
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        return client
    except KeyError:
        st.error("MONGO_URI not found in secrets. Please configure .streamlit/secrets.toml")
        return None
    except Exception as e:
        st.error(f"MongoDB connection failed: {e}")
        return None


@st.cache_data(ttl=3600)
def load_production_2021():
    """
    Load 2021 production data from MongoDB.

    IMPORTANT: This replaces CSV downloads. NO CSV files should be used!

    Returns:
        pd.DataFrame: Production data with columns:
            - priceArea
            - productionGroup
            - startTime
            - quantityKwh
    """
    client = get_mongo_client()
    if not client:
        st.warning("MongoDB not connected. Cannot load data.")
        return pd.DataFrame()

    try:
        db = client['ind320']
        collection = db['production_2021']

        # Query all records
        cursor = collection.find({}, {'_id': 0})
        df = pd.DataFrame(list(cursor))

        if df.empty:
            st.warning("No data found in MongoDB collection: production_2021")
            return pd.DataFrame()

        # Convert timestamps (remove timezone for compatibility)
        if 'startTime' in df.columns:
            df['startTime'] = pd.to_datetime(df['startTime']).dt.tz_localize(None)

        # Filter out unspecified/x/× production groups (professor feedback fix)
        if 'productionGroup' in df.columns:
            df = df[~df['productionGroup'].isin(['unspecified', 'x', 'Unspecified', 'X', '×', '*'])]

        st.sidebar.success(f"✅ Loaded {len(df):,} records from MongoDB")
        return df

    except Exception as e:
        st.error(f"Error loading from MongoDB: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_monthly_aggregation():
    """
    Get monthly aggregated production data from MongoDB.

    Returns:
        pd.DataFrame: Monthly aggregated data
    """
    df = load_production_2021()

    if df.empty:
        return pd.DataFrame()

    # Add month column
    df['month'] = df['startTime'].dt.month

    # Aggregate by month, price area, and production group
    monthly = df.groupby(
        ['priceArea', 'month', 'productionGroup']
    )['quantityKwh'].sum().reset_index()

    return monthly


@st.cache_data(ttl=3600)
def get_price_areas() -> List[str]:
    """
    Get list of available price areas from MongoDB.

    Returns:
        List[str]: List of price area codes (e.g., ['NO1', 'NO2', ...])
    """
    df = load_production_2021()

    if df.empty:
        return ['NO1', 'NO2', 'NO3', 'NO4', 'NO5']  # Fallback

    return sorted(df['priceArea'].unique().tolist())


@st.cache_data(ttl=3600)
def get_production_groups() -> List[str]:
    """
    Get list of available production groups from MongoDB.

    Returns:
        List[str]: List of production groups (e.g., ['Hydro', 'Wind', ...])
    """
    df = load_production_2021()

    if df.empty:
        return ['Hydro', 'Wind', 'Thermal', 'Solar']  # Fallback

    return sorted(df['productionGroup'].unique().tolist())


def check_mongodb_connection() -> dict:
    """
    Check MongoDB connection status.

    Returns:
        dict: Status information
    """
    client = get_mongo_client()

    if not client:
        return {
            'status': 'disconnected',
            'message': 'Failed to connect to MongoDB'
        }

    try:
        # Get server info
        server_info = client.server_info()

        # Count documents
        db = client['ind320']
        collection = db['production_2021']
        count = collection.count_documents({})

        return {
            'status': 'connected',
            'message': f'Connected to MongoDB',
            'version': server_info.get('version', 'unknown'),
            'document_count': count
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error: {str(e)}'
        }


# ============================================================================
# ASSESSMENT 4 - NEW FUNCTIONS FOR 2022-2024 DATA AND CONSUMPTION
# ============================================================================

@st.cache_data(ttl=3600)
def load_production_all_years(start_year: Optional[int] = None, end_year: Optional[int] = None):
    """
    Load production data for all years (2021-2024) from MongoDB.

    Args:
        start_year: Filter from this year (inclusive)
        end_year: Filter to this year (inclusive)

    Returns:
        pd.DataFrame: Production data with columns:
            - priceArea
            - productionGroup
            - startTime
            - quantityMWh (or quantityKwh)
    """
    client = get_mongo_client()
    if not client:
        st.warning("MongoDB not connected. Cannot load data.")
        return pd.DataFrame()

    try:
        db = client['ind320']

        # Load from both collections
        dfs = []
        for collection_name in ['elhub_production_2021', 'elhub_production_2022_2024']:
            collection = db[collection_name]
            cursor = collection.find({}, {'_id': 0})
            df_temp = pd.DataFrame(list(cursor))
            if not df_temp.empty:
                dfs.append(df_temp)

        if not dfs:
            st.warning("No production data found in MongoDB")
            return pd.DataFrame()

        # Combine dataframes
        df = pd.concat(dfs, ignore_index=True)

        # Convert timestamps
        if 'startTime' in df.columns:
            df['startTime'] = pd.to_datetime(df['startTime']).dt.tz_localize(None)

        # Standardize column names (quantityMWh or quantityKwh)
        if 'quantityMWh' in df.columns and 'quantityKwh' not in df.columns:
            df['quantityKwh'] = df['quantityMWh'] * 1000  # Convert MWh to kWh

        # Filter by year if specified
        if start_year or end_year:
            if start_year:
                df = df[df['startTime'].dt.year >= start_year]
            if end_year:
                df = df[df['startTime'].dt.year <= end_year]

        # Filter out invalid production groups
        if 'productionGroup' in df.columns:
            df = df[~df['productionGroup'].isin(['unspecified', 'x', 'Unspecified', 'X', '×', '*'])]

        return df

    except Exception as e:
        st.error(f"Error loading production data: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_consumption_all_years(start_year: Optional[int] = None, end_year: Optional[int] = None):
    """
    Load consumption data for all years (2021-2024) from MongoDB.

    Args:
        start_year: Filter from this year (inclusive)
        end_year: Filter to this year (inclusive)

    Returns:
        pd.DataFrame: Consumption data with columns:
            - priceArea
            - consumptionGroup
            - startTime
            - quantityMWh
    """
    client = get_mongo_client()
    if not client:
        st.warning("MongoDB not connected. Cannot load data.")
        return pd.DataFrame()

    try:
        db = client['ind320']

        # Load from both collections
        dfs = []
        for collection_name in ['elhub_consumption_2021', 'elhub_consumption_2022_2024']:
            collection = db[collection_name]
            cursor = collection.find({}, {'_id': 0})
            df_temp = pd.DataFrame(list(cursor))
            if not df_temp.empty:
                dfs.append(df_temp)

        if not dfs:
            st.warning("No consumption data found in MongoDB")
            return pd.DataFrame()

        # Combine dataframes
        df = pd.concat(dfs, ignore_index=True)

        # Convert timestamps
        if 'startTime' in df.columns:
            df['startTime'] = pd.to_datetime(df['startTime']).dt.tz_localize(None)

        # Standardize column names
        if 'quantityMWh' in df.columns and 'quantityKwh' not in df.columns:
            df['quantityKwh'] = df['quantityMWh'] * 1000  # Convert MWh to kWh

        # Filter by year if specified
        if start_year or end_year:
            if start_year:
                df = df[df['startTime'].dt.year >= start_year]
            if end_year:
                df = df[df['startTime'].dt.year <= end_year]

        # Filter out invalid consumption groups
        if 'consumptionGroup' in df.columns:
            df = df[~df['consumptionGroup'].isin(['unspecified', 'x', 'Unspecified', 'X', '×', '*'])]

        return df

    except Exception as e:
        st.error(f"Error loading consumption data: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_aggregated_by_area_timerange(
    data_type: str,  # 'production' or 'consumption'
    start_date: str,
    end_date: str,
    group_column: Optional[str] = None
):
    """
    Get aggregated data by price area for a time range.
    Used for map visualization (choropleth).

    Args:
        data_type: 'production' or 'consumption'
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        group_column: Specific production/consumption group to filter

    Returns:
        pd.DataFrame: Aggregated data with columns:
            - priceArea
            - mean_quantity
            - total_quantity
    """
    if data_type == 'production':
        df = load_production_all_years()
        group_col = 'productionGroup'
    else:
        df = load_consumption_all_years()
        group_col = 'consumptionGroup'

    if df.empty:
        return pd.DataFrame()

    # Filter by date range
    df = df[(df['startTime'] >= start_date) & (df['startTime'] <= end_date)]

    # Filter by group if specified
    if group_column and group_col in df.columns:
        df = df[df[group_col] == group_column]

    # Get quantity column name
    qty_col = 'quantityKwh' if 'quantityKwh' in df.columns else 'quantityMWh'

    # Aggregate by price area
    aggregated = df.groupby('priceArea').agg({
        qty_col: ['mean', 'sum']
    }).reset_index()

    aggregated.columns = ['priceArea', 'mean_quantity', 'total_quantity']

    return aggregated


@st.cache_data(ttl=3600)
def get_consumption_groups() -> List[str]:
    """
    Get list of available consumption groups from MongoDB.

    Returns:
        List[str]: List of consumption groups
    """
    df = load_consumption_all_years()

    if df.empty:
        return ['Household', 'Industry', 'Service']  # Fallback

    if 'consumptionGroup' in df.columns:
        return sorted(df['consumptionGroup'].unique().tolist())

    return []
