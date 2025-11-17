"""
Cassandra Database Client for Streamlit Application
IND320 Assessment 4

This module provides a clean interface for accessing energy data from Cassandra.
Compatible with the existing Streamlit pages (can replace MongoDB calls).
"""

import streamlit as st
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict


# Cassandra Configuration
CASSANDRA_HOSTS = ['127.0.0.1']
CASSANDRA_PORT = 9042
KEYSPACE = 'ind320'


@st.cache_resource
def get_cassandra_session():
    """
    Create and cache Cassandra session.

    Returns:
        session: Cassandra session object or None if connection fails
    """
    try:
        cluster = Cluster(CASSANDRA_HOSTS, port=CASSANDRA_PORT)
        session = cluster.connect(KEYSPACE)
        return session
    except Exception as e:
        st.error(f"Failed to connect to Cassandra: {e}")
        return None


def check_connection():
    """
    Check if Cassandra connection is working.

    Returns:
        dict: Connection status information
    """
    try:
        session = get_cassandra_session()
        if session:
            result = session.execute("SELECT release_version FROM system.local")
            version = result.one()[0]
            return {
                'status': 'connected',
                'version': version,
                'keyspace': KEYSPACE,
                'hosts': CASSANDRA_HOSTS
            }
        else:
            return {'status': 'disconnected', 'error': 'Failed to create session'}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}


@st.cache_data(ttl=3600)
def get_collection_count(table_name: str) -> int:
    """
    Get the total number of records in a table.

    Parameters:
        table_name: Name of the Cassandra table

    Returns:
        int: Record count
    """
    try:
        session = get_cassandra_session()
        if not session:
            return 0

        # Note: COUNT(*) can be slow in Cassandra, use sparingly
        query = f"SELECT COUNT(*) FROM {table_name}"
        result = session.execute(query)
        count = result.one()[0]
        return count
    except Exception as e:
        st.warning(f"Could not count records in {table_name}: {e}")
        return 0


@st.cache_data(ttl=3600)
def fetch_consumption_data(
    collection_name: str,
    start_date: datetime,
    end_date: datetime,
    price_area: Optional[str] = None,
    consumption_group: Optional[str] = None
) -> pd.DataFrame:
    """
    Fetch consumption data from Cassandra.

    Parameters:
        collection_name: Table name (elhub_consumption_2021 or elhub_consumption_2022_2024)
        start_date: Start datetime
        end_date: End datetime
        price_area: Optional price area filter (NO1, NO2, etc.)
        consumption_group: Optional consumption group filter

    Returns:
        pd.DataFrame: Consumption data
    """
    try:
        session = get_cassandra_session()
        if not session:
            return pd.DataFrame()

        # Build query based on filters
        if price_area and consumption_group:
            query = f"""
                SELECT * FROM {collection_name}
                WHERE priceArea = %s
                AND consumptionGroup = %s
                AND startTime >= %s
                AND startTime <= %s
                ALLOW FILTERING
            """
            params = (price_area, consumption_group, start_date, end_date)
        else:
            query = f"""
                SELECT * FROM {collection_name}
                WHERE startTime >= %s
                AND startTime <= %s
                ALLOW FILTERING
            """
            params = (start_date, end_date)

        result = session.execute(query, params)
        df = pd.DataFrame(list(result))

        if not df.empty:
            # Convert timestamp columns
            if 'starttime' in df.columns:
                df['startTime'] = pd.to_datetime(df['starttime'])
                df['endTime'] = pd.to_datetime(df['endtime'])
                df.drop(['starttime', 'endtime'], axis=1, inplace=True)

        return df

    except Exception as e:
        st.warning(f"Error fetching consumption data: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def fetch_production_data(
    collection_name: str,
    start_date: datetime,
    end_date: datetime,
    price_area: Optional[str] = None,
    production_group: Optional[str] = None
) -> pd.DataFrame:
    """
    Fetch production data from Cassandra.

    Parameters:
        collection_name: Table name (elhub_production_2022_2024)
        start_date: Start datetime
        end_date: End datetime
        price_area: Optional price area filter (NO1, NO2, etc.)
        production_group: Optional production group filter

    Returns:
        pd.DataFrame: Production data
    """
    try:
        session = get_cassandra_session()
        if not session:
            return pd.DataFrame()

        # Build query based on filters
        if price_area and production_group:
            query = f"""
                SELECT * FROM {collection_name}
                WHERE priceArea = %s
                AND productionGroup = %s
                AND startTime >= %s
                AND startTime <= %s
                ALLOW FILTERING
            """
            params = (price_area, production_group, start_date, end_date)
        else:
            query = f"""
                SELECT * FROM {collection_name}
                WHERE startTime >= %s
                AND startTime <= %s
                ALLOW FILTERING
            """
            params = (start_date, end_date)

        result = session.execute(query, params)
        df = pd.DataFrame(list(result))

        if not df.empty:
            # Convert timestamp columns
            if 'starttime' in df.columns:
                df['startTime'] = pd.to_datetime(df['starttime'])
                df['endTime'] = pd.to_datetime(df['endtime'])
                df.drop(['starttime', 'endtime'], axis=1, inplace=True)

        return df

    except Exception as e:
        st.warning(f"Error fetching production data: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_available_groups(collection_name: str, group_type: str = 'consumption') -> List[str]:
    """
    Get list of available consumption or production groups.

    Parameters:
        collection_name: Table name
        group_type: 'consumption' or 'production'

    Returns:
        List[str]: Available groups
    """
    try:
        session = get_cassandra_session()
        if not session:
            return []

        column_name = 'consumptionGroup' if group_type == 'consumption' else 'productionGroup'

        query = f"SELECT DISTINCT {column_name} FROM {collection_name}"
        result = session.execute(query)

        groups = [row[0] for row in result if row[0]]
        return sorted(groups)

    except Exception as e:
        st.warning(f"Error fetching groups: {e}")
        # Return default values as fallback
        if group_type == 'consumption':
            return ['Residential', 'Commercial', 'Industrial', 'Other']
        else:
            return ['Hydro', 'Wind', 'Thermal', 'Solar']


@st.cache_data(ttl=3600)
def get_available_price_areas(collection_name: str) -> List[str]:
    """
    Get list of available price areas.

    Parameters:
        collection_name: Table name

    Returns:
        List[str]: Available price areas
    """
    try:
        session = get_cassandra_session()
        if not session:
            return []

        query = f"SELECT DISTINCT priceArea FROM {collection_name}"
        result = session.execute(query)

        areas = [row[0] for row in result if row[0]]
        return sorted(areas)

    except Exception as e:
        st.warning(f"Error fetching price areas: {e}")
        return ['NO1', 'NO2', 'NO3', 'NO4', 'NO5']


def get_date_range(collection_name: str) -> Dict[str, datetime]:
    """
    Get the min and max dates available in a collection.

    Parameters:
        collection_name: Table name

    Returns:
        dict: {'min_date': datetime, 'max_date': datetime}
    """
    try:
        session = get_cassandra_session()
        if not session:
            return {'min_date': None, 'max_date': None}

        # Note: MIN/MAX aggregations might not be efficient in Cassandra
        # This is a simplified approach
        query = f"SELECT startTime FROM {collection_name} LIMIT 1000"
        result = session.execute(query)

        dates = [row.starttime for row in result if hasattr(row, 'starttime')]

        if dates:
            return {
                'min_date': min(dates),
                'max_date': max(dates)
            }
        else:
            return {'min_date': None, 'max_date': None}

    except Exception as e:
        st.warning(f"Error fetching date range: {e}")
        return {'min_date': None, 'max_date': None}


# Alias functions for MongoDB compatibility
def get_mongo_client():
    """Compatibility function - returns Cassandra session instead."""
    return get_cassandra_session()


def get_database(client, db_name='ind320'):
    """Compatibility function - returns client (Cassandra session)."""
    return client
