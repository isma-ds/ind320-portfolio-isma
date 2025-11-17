#!/usr/bin/env python3
"""
Fetch real energy data from Elhub API for Assessment 4.

This script retrieves actual Norwegian electricity production and consumption data
from the public Elhub API (no authentication required).

API Endpoints:
- Consumption: https://api.elhub.no/energy-data/v0/price-areas?dataset=CONSUMPTION_PER_GROUP_MBA_HOUR
- Production: https://api.elhub.no/energy-data/v0/price-areas?dataset=PRODUCTION_PER_GROUP_MBA_HOUR

Data Structure:
- Price Areas: NO1, NO2, NO3, NO4, NO5
- Time Resolution: Hourly
- Format: JSON with nested data arrays
"""

import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import sys

# API Configuration
BASE_URL = "https://api.elhub.no/energy-data/v0"
ENTITY = "price-areas"

# Datasets
CONSUMPTION_DATASET = "CONSUMPTION_PER_GROUP_MBA_HOUR"
PRODUCTION_DATASET = "PRODUCTION_PER_GROUP_MBA_HOUR"

# Norwegian Price Areas
PRICE_AREAS = ["NO1", "NO2", "NO3", "NO4", "NO5"]


def fetch_elhub_data(dataset, start_date=None, end_date=None, price_area=None):
    """
    Fetch data from Elhub API.

    Parameters:
        dataset (str): Dataset name (CONSUMPTION_PER_GROUP_MBA_HOUR or PRODUCTION_PER_GROUP_MBA_HOUR)
        start_date (str): Optional start date filter (ISO format)
        end_date (str): Optional end date filter (ISO format)
        price_area (str): Optional price area filter (NO1, NO2, etc.)

    Returns:
        dict: JSON response from API
    """
    url = f"{BASE_URL}/{ENTITY}"
    params = {"dataset": dataset}

    # Add optional filters if provided
    if start_date:
        params["startTime"] = start_date
    if end_date:
        params["endTime"] = end_date
    if price_area:
        params["priceArea"] = price_area

    print(f"Fetching {dataset}...")
    print(f"URL: {url}")
    print(f"Params: {params}")

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch data: {e}")
        return None


def parse_elhub_response(response_data, data_type):
    """
    Parse Elhub API response into pandas DataFrame.

    Parameters:
        response_data (dict): JSON response from API
        data_type (str): 'consumption' or 'production'

    Returns:
        pd.DataFrame: Parsed data
    """
    if not response_data or "data" not in response_data:
        print("[WARNING] No data found in response")
        return pd.DataFrame()

    records = []

    for item in response_data.get("data", []):
        attributes = item.get("attributes", {})

        # Extract common fields
        record = {
            "startTime": attributes.get("startTime"),
            "endTime": attributes.get("endTime"),
            "priceArea": attributes.get("priceArea"),
            "quantityKwh": float(attributes.get("quantityKwh", 0)),
            "lastUpdatedTime": attributes.get("lastUpdatedTime"),
        }

        # Add type-specific fields
        if data_type == "consumption":
            record["consumptionGroup"] = attributes.get("consumptionGroup")
            record["meteringPointCount"] = attributes.get("meteringPointCount")
        elif data_type == "production":
            record["productionGroup"] = attributes.get("productionGroup")

        records.append(record)

    df = pd.DataFrame(records)

    # Convert timestamps to datetime
    if not df.empty and "startTime" in df.columns:
        df["startTime"] = pd.to_datetime(df["startTime"])
        df["endTime"] = pd.to_datetime(df["endTime"])
        df["lastUpdatedTime"] = pd.to_datetime(df["lastUpdatedTime"])

    return df


def fetch_consumption_data(year_start, year_end):
    """
    Fetch consumption data for specified year range.

    Parameters:
        year_start (int): Start year (e.g., 2021)
        year_end (int): End year (e.g., 2024)

    Returns:
        pd.DataFrame: Combined consumption data
    """
    all_data = []

    for year in range(year_start, year_end + 1):
        start_date = f"{year}-01-01T00:00:00Z"
        end_date = f"{year}-12-31T23:59:59Z"

        print(f"\n[FETCH] Consumption data for {year}...")

        response = fetch_elhub_data(
            dataset=CONSUMPTION_DATASET,
            start_date=start_date,
            end_date=end_date
        )

        if response:
            df = parse_elhub_response(response, "consumption")
            if not df.empty:
                print(f"[OK] Retrieved {len(df)} consumption records for {year}")
                all_data.append(df)
            else:
                print(f"[WARNING] No consumption data for {year}")

        # Rate limiting: wait 1 second between requests
        time.sleep(1)

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        print(f"\n[SUMMARY] Total consumption records: {len(combined)}")
        return combined
    else:
        print("[ERROR] No consumption data retrieved")
        return pd.DataFrame()


def fetch_production_data(year_start, year_end):
    """
    Fetch production data for specified year range.

    Parameters:
        year_start (int): Start year (e.g., 2022)
        year_end (int): End year (e.g., 2024)

    Returns:
        pd.DataFrame: Combined production data
    """
    all_data = []

    for year in range(year_start, year_end + 1):
        start_date = f"{year}-01-01T00:00:00Z"
        end_date = f"{year}-12-31T23:59:59Z"

        print(f"\n[FETCH] Production data for {year}...")

        response = fetch_elhub_data(
            dataset=PRODUCTION_DATASET,
            start_date=start_date,
            end_date=end_date
        )

        if response:
            df = parse_elhub_response(response, "production")
            if not df.empty:
                print(f"[OK] Retrieved {len(df)} production records for {year}")
                all_data.append(df)
            else:
                print(f"[WARNING] No production data for {year}")

        # Rate limiting: wait 1 second between requests
        time.sleep(1)

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        print(f"\n[SUMMARY] Total production records: {len(combined)}")
        return combined
    else:
        print("[ERROR] No production data retrieved")
        return pd.DataFrame()


def save_to_csv(df, filename):
    """Save DataFrame to CSV file."""
    if df.empty:
        print(f"[WARNING] Empty DataFrame, skipping save for {filename}")
        return

    filepath = f"data/{filename}"
    df.to_csv(filepath, index=False)
    print(f"[OK] Saved {len(df)} records to {filepath}")


def save_to_json(df, filename):
    """Save DataFrame to JSON file (MongoDB-ready format)."""
    if df.empty:
        print(f"[WARNING] Empty DataFrame, skipping save for {filename}")
        return

    filepath = f"data/{filename}"

    # Convert to dict format suitable for MongoDB
    records = df.to_dict('records')

    # Convert Timestamp objects to ISO strings for JSON serialization
    for record in records:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
            elif isinstance(value, pd.Timestamp):
                record[key] = value.isoformat()

    with open(filepath, 'w') as f:
        json.dump(records, f, indent=2, default=str)

    print(f"[OK] Saved {len(records)} records to {filepath}")


def main():
    """Main execution function."""
    print("=" * 70)
    print("ELHUB API DATA FETCHER - Assessment 4")
    print("=" * 70)
    print("\nFetching real Norwegian electricity data from public Elhub API...")
    print("No authentication required - public access API")

    # Fetch consumption data for 2021
    print("\n" + "=" * 70)
    print("STEP 1: Fetch 2021 Consumption Data")
    print("=" * 70)
    consumption_2021 = fetch_consumption_data(2021, 2021)
    if not consumption_2021.empty:
        save_to_csv(consumption_2021, "elhub_consumption_2021.csv")
        save_to_json(consumption_2021, "elhub_consumption_2021.json")

    # Fetch consumption data for 2022-2024
    print("\n" + "=" * 70)
    print("STEP 2: Fetch 2022-2024 Consumption Data")
    print("=" * 70)
    consumption_2022_2024 = fetch_consumption_data(2022, 2024)
    if not consumption_2022_2024.empty:
        save_to_csv(consumption_2022_2024, "elhub_consumption_2022_2024.csv")
        save_to_json(consumption_2022_2024, "elhub_consumption_2022_2024.json")

    # Fetch production data for 2022-2024
    print("\n" + "=" * 70)
    print("STEP 3: Fetch 2022-2024 Production Data")
    print("=" * 70)
    production_2022_2024 = fetch_production_data(2022, 2024)
    if not production_2022_2024.empty:
        save_to_csv(production_2022_2024, "elhub_production_2022_2024.csv")
        save_to_json(production_2022_2024, "elhub_production_2022_2024.json")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Consumption 2021: {len(consumption_2021) if not consumption_2021.empty else 0} records")
    print(f"Consumption 2022-2024: {len(consumption_2022_2024) if not consumption_2022_2024.empty else 0} records")
    print(f"Production 2022-2024: {len(production_2022_2024) if not production_2022_2024.empty else 0} records")

    total_records = (
        (len(consumption_2021) if not consumption_2021.empty else 0) +
        (len(consumption_2022_2024) if not consumption_2022_2024.empty else 0) +
        (len(production_2022_2024) if not production_2022_2024.empty else 0)
    )
    print(f"\nTotal records fetched: {total_records}")

    if total_records > 0:
        print("\n[SUCCESS] Real Elhub data successfully downloaded!")
        print("Next step: Upload to MongoDB using scripts/upload_to_mongodb.py")
    else:
        print("\n[ERROR] No data was fetched. Check API availability.")
        sys.exit(1)


if __name__ == "__main__":
    main()
