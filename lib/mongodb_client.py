"""
MongoDB client for Streamlit pages - Assessment 2/3
Replaces all CSV downloads with MongoDB queries.

CRITICAL: This file ensures NO CSV downloads in Streamlit app.
All data must come from MongoDB to pass Assessment 2.
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
