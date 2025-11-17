#!/usr/bin/env python3
"""
Upload Elhub energy data to Cassandra database.

This script uploads real or synthetic energy data to a local Cassandra cluster
running in Docker containers.

Prerequisites:
- Docker Compose cluster running (docker-compose up -d)
- Cassandra nodes healthy and initialized
- Data files in data/ directory (CSV format)
"""

import sys
import time
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import BatchStatement, SimpleStatement
from cassandra import ConsistencyLevel
import pandas as pd
from datetime import datetime


# Cassandra Configuration
CASSANDRA_HOSTS = ['127.0.0.1']
CASSANDRA_PORT = 9042
KEYSPACE = 'ind320'


def wait_for_cassandra(max_retries=30, retry_delay=10):
    """
    Wait for Cassandra cluster to be ready.

    Parameters:
        max_retries: Maximum number of connection attempts
        retry_delay: Seconds to wait between retries

    Returns:
        bool: True if connection successful, False otherwise
    """
    print(f"Waiting for Cassandra cluster at {CASSANDRA_HOSTS[0]}:{CASSANDRA_PORT}...")

    for attempt in range(1, max_retries + 1):
        try:
            cluster = Cluster(CASSANDRA_HOSTS, port=CASSANDRA_PORT)
            session = cluster.connect()
            session.execute("SELECT release_version FROM system.local")
            version = session.execute("SELECT release_version FROM system.local").one()[0]
            print(f"[OK] Connected to Cassandra {version}")
            cluster.shutdown()
            return True
        except Exception as e:
            print(f"[RETRY {attempt}/{max_retries}] Cassandra not ready: {e}")
            if attempt < max_retries:
                print(f"Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)

    print("[ERROR] Could not connect to Cassandra after maximum retries")
    return False


def connect_to_cassandra():
    """
    Establish connection to Cassandra cluster.

    Returns:
        tuple: (cluster, session) objects
    """
    try:
        cluster = Cluster(CASSANDRA_HOSTS, port=CASSANDRA_PORT)
        session = cluster.connect(KEYSPACE)
        print(f"[OK] Connected to keyspace '{KEYSPACE}'")
        return cluster, session
    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")
        sys.exit(1)


def create_keyspace_and_tables(session):
    """
    Create keyspace and tables if they don't exist.

    Parameters:
        session: Cassandra session object
    """
    print("\n[SETUP] Creating keyspace and tables...")

    # Create keyspace
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS ind320
        WITH replication = {
            'class': 'SimpleStrategy',
            'replication_factor': 3
        }
    """)
    print("[OK] Keyspace 'ind320' ready")

    # Use keyspace
    session.set_keyspace('ind320')

    # Create tables
    tables = {
        'elhub_consumption_2021': """
            CREATE TABLE IF NOT EXISTS elhub_consumption_2021 (
                startTime timestamp,
                endTime timestamp,
                priceArea text,
                consumptionGroup text,
                quantityKwh double,
                meteringPointCount int,
                lastUpdatedTime timestamp,
                PRIMARY KEY ((priceArea, consumptionGroup), startTime)
            ) WITH CLUSTERING ORDER BY (startTime DESC)
        """,
        'elhub_consumption_2022_2024': """
            CREATE TABLE IF NOT EXISTS elhub_consumption_2022_2024 (
                startTime timestamp,
                endTime timestamp,
                priceArea text,
                consumptionGroup text,
                quantityKwh double,
                meteringPointCount int,
                lastUpdatedTime timestamp,
                PRIMARY KEY ((priceArea, consumptionGroup), startTime)
            ) WITH CLUSTERING ORDER BY (startTime DESC)
        """,
        'elhub_production_2022_2024': """
            CREATE TABLE IF NOT EXISTS elhub_production_2022_2024 (
                startTime timestamp,
                endTime timestamp,
                priceArea text,
                productionGroup text,
                quantityKwh double,
                lastUpdatedTime timestamp,
                PRIMARY KEY ((priceArea, productionGroup), startTime)
            ) WITH CLUSTERING ORDER BY (startTime DESC)
        """
    }

    for table_name, create_statement in tables.items():
        session.execute(create_statement)
        print(f"[OK] Table '{table_name}' ready")


def upload_consumption_data(session, csv_file, table_name):
    """
    Upload consumption data from CSV to Cassandra.

    Parameters:
        session: Cassandra session
        csv_file: Path to CSV file
        table_name: Target Cassandra table

    Returns:
        int: Number of records uploaded
    """
    print(f"\n[UPLOAD] Loading {csv_file}...")

    try:
        df = pd.read_csv(csv_file)
        print(f"[OK] Loaded {len(df)} records from CSV")

        # Convert timestamp columns to datetime
        df['startTime'] = pd.to_datetime(df['startTime'])
        df['endTime'] = pd.to_datetime(df['endTime'])
        df['lastUpdatedTime'] = pd.to_datetime(df['lastUpdatedTime'])

        # Prepare insert statement
        insert_stmt = session.prepare(f"""
            INSERT INTO {table_name}
            (startTime, endTime, priceArea, consumptionGroup, quantityKwh, meteringPointCount, lastUpdatedTime)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """)

        # Batch upload (100 records per batch)
        batch_size = 100
        total_uploaded = 0

        for i in range(0, len(df), batch_size):
            batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)

            for _, row in df.iloc[i:i+batch_size].iterrows():
                batch.add(insert_stmt, (
                    row['startTime'],
                    row['endTime'],
                    row['priceArea'],
                    row['consumptionGroup'],
                    float(row['quantityKwh']),
                    int(row.get('meteringPointCount', 0)),
                    row['lastUpdatedTime']
                ))

            session.execute(batch)
            total_uploaded += len(df.iloc[i:i+batch_size])

            if total_uploaded % 1000 == 0:
                print(f"[PROGRESS] Uploaded {total_uploaded}/{len(df)} records...")

        print(f"[OK] Successfully uploaded {total_uploaded} records to {table_name}")
        return total_uploaded

    except FileNotFoundError:
        print(f"[WARNING] File not found: {csv_file}")
        return 0
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        return 0


def upload_production_data(session, csv_file, table_name):
    """
    Upload production data from CSV to Cassandra.

    Parameters:
        session: Cassandra session
        csv_file: Path to CSV file
        table_name: Target Cassandra table

    Returns:
        int: Number of records uploaded
    """
    print(f"\n[UPLOAD] Loading {csv_file}...")

    try:
        df = pd.read_csv(csv_file)
        print(f"[OK] Loaded {len(df)} records from CSV")

        # Convert timestamp columns to datetime
        df['startTime'] = pd.to_datetime(df['startTime'])
        df['endTime'] = pd.to_datetime(df['endTime'])
        df['lastUpdatedTime'] = pd.to_datetime(df['lastUpdatedTime'])

        # Prepare insert statement
        insert_stmt = session.prepare(f"""
            INSERT INTO {table_name}
            (startTime, endTime, priceArea, productionGroup, quantityKwh, lastUpdatedTime)
            VALUES (?, ?, ?, ?, ?, ?)
        """)

        # Batch upload (100 records per batch)
        batch_size = 100
        total_uploaded = 0

        for i in range(0, len(df), batch_size):
            batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)

            for _, row in df.iloc[i:i+batch_size].iterrows():
                batch.add(insert_stmt, (
                    row['startTime'],
                    row['endTime'],
                    row['priceArea'],
                    row['productionGroup'],
                    float(row['quantityKwh']),
                    row['lastUpdatedTime']
                ))

            session.execute(batch)
            total_uploaded += len(df.iloc[i:i+batch_size])

            if total_uploaded % 1000 == 0:
                print(f"[PROGRESS] Uploaded {total_uploaded}/{len(df)} records...")

        print(f"[OK] Successfully uploaded {total_uploaded} records to {table_name}")
        return total_uploaded

    except FileNotFoundError:
        print(f"[WARNING] File not found: {csv_file}")
        return 0
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        return 0


def verify_data(session):
    """
    Verify uploaded data by counting records in each table.

    Parameters:
        session: Cassandra session
    """
    print("\n" + "="*70)
    print("DATA VERIFICATION")
    print("="*70)

    tables = [
        'elhub_consumption_2021',
        'elhub_consumption_2022_2024',
        'elhub_production_2022_2024'
    ]

    total_records = 0

    for table in tables:
        try:
            # Count records (note: COUNT(*) can be slow in Cassandra)
            result = session.execute(f"SELECT COUNT(*) FROM {table}")
            count = result.one()[0]
            print(f"{table}: {count:,} records")
            total_records += count
        except Exception as e:
            print(f"{table}: [ERROR] {e}")

    print(f"\nTotal records in Cassandra: {total_records:,}")


def main():
    """Main execution function."""
    print("="*70)
    print("CASSANDRA DATA UPLOADER - IND320 Assessment 4")
    print("="*70)

    # Wait for Cassandra to be ready
    if not wait_for_cassandra():
        print("\n[ERROR] Cassandra cluster is not available")
        print("Please ensure Docker Compose is running: docker-compose up -d")
        sys.exit(1)

    # Connect to Cassandra
    cluster, session = connect_to_cassandra()

    try:
        # Create keyspace and tables
        create_keyspace_and_tables(session)

        # Upload data files
        total_uploaded = 0

        # Upload consumption 2021
        count = upload_consumption_data(
            session,
            'data/elhub_consumption_2021.csv',
            'elhub_consumption_2021'
        )
        total_uploaded += count

        # Upload consumption 2022-2024
        count = upload_consumption_data(
            session,
            'data/elhub_consumption_2022_2024.csv',
            'elhub_consumption_2022_2024'
        )
        total_uploaded += count

        # Upload production 2022-2024
        count = upload_production_data(
            session,
            'data/elhub_production_2022_2024.csv',
            'elhub_production_2022_2024'
        )
        total_uploaded += count

        # Verify data
        verify_data(session)

        # Summary
        print("\n" + "="*70)
        print("UPLOAD COMPLETE")
        print("="*70)
        print(f"Total records uploaded: {total_uploaded:,}")
        print(f"Keyspace: {KEYSPACE}")
        print(f"Replication factor: 3")
        print(f"Cluster nodes: {len(CASSANDRA_HOSTS)}")

    finally:
        cluster.shutdown()
        print("\n[OK] Connection closed")


if __name__ == "__main__":
    main()
