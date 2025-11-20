#!/usr/bin/env python3
"""
Fetch 2021 Production Data from Real Elhub API
Assessment 2 Requirement

CRITICAL: This replaces CSV downloads with proper API usage.

Instructor feedback:
"You are downloading CSV files instead of using the Python API for elhub."

This script uses the CORRECT API endpoint:
https://api.elhub.no/energy-data/v0/price-areas

NOT the CSV download URL!
"""

import requests
import pandas as pd
import json
from datetime import datetime
import time

def fetch_elhub_2021_production():
    """
    Fetch 2021 production data from Elhub API.

    Uses PRODUCTION_PER_GROUP_MBA_HOUR dataset.
    Returns JSON response, NOT CSV file!
    """

    print("="*70)
    print("FETCHING 2021 PRODUCTION DATA FROM ELHUB API")
    print("="*70)
    print()

    # CORRECT API endpoint (NOT CSV download!)
    url = "https://api.elhub.no/energy-data/v0/price-areas"

    params = {
        "dataset": "PRODUCTION_PER_GROUP_MBA_HOUR",
        "startTime": "2021-01-01T00:00:00Z",
        "endTime": "2021-12-31T23:59:59Z"
    }

    print(f"API Endpoint: {url}")
    print(f"Dataset: {params['dataset']}")
    print(f"Time Range: 2021-01-01 to 2021-12-31")
    print()
    print("Fetching data... (this may take 30-60 seconds)")
    print()

    try:
        response = requests.get(url, params=params, timeout=120)
        response.raise_for_status()

        print(f"[OK] API Response Status: {response.status_code}")
        print(f"[OK] Response Type: {response.headers.get('content-type', 'unknown')}")
        print()

        # Parse JSON response
        data = response.json()

        # Extract production data from JSON structure
        # NOTE: API returns array of price areas, need to collect from ALL of them
        if 'data' in data and len(data['data']) > 0:
            all_production_data = []

            # Loop through all price areas in response
            for price_area_data in data['data']:
                attributes = price_area_data.get('attributes', {})

                # Check if productionPerGroupMbaHour exists
                if 'productionPerGroupMbaHour' in attributes:
                    production_list = attributes['productionPerGroupMbaHour']

                    if production_list:  # Only if not empty
                        all_production_data.extend(production_list)

            # Convert combined data to DataFrame
            if all_production_data:
                df = pd.DataFrame(all_production_data)

                print(f"[OK] Successfully fetched {len(df):,} records")
                print()

                # Check actual date range
                if 'startTime' in df.columns:
                    df['startTime'] = pd.to_datetime(df['startTime'])
                    actual_start = df['startTime'].min()
                    actual_end = df['startTime'].max()
                    print(f"[INFO] Actual date range in data: {actual_start} to {actual_end}")

                    # Check if we got 2021 data as requested
                    if actual_start.year != 2021 or actual_end.year != 2021:
                        print(f"[WARNING] Requested 2021 data but got {actual_start.year}-{actual_end.year}")
                        print(f"[WARNING] Elhub API may only have recent data available")
                    print()

                print("Data Structure:")
                print(f"  Columns: {df.columns.tolist()}")
                print(f"  Shape: {df.shape}")
                print()
                print("First 5 rows:")
                print(df.head())
                print()

                # Check for production groups
                if 'productionGroup' in df.columns:
                    groups = df['productionGroup'].unique()
                    print(f"Production Groups: {groups.tolist()}")
                    print()

                    # Check for "unspecified" issue
                    unspecified = df[df['productionGroup'].str.contains('unspecified', case=False, na=False)]
                    if len(unspecified) > 0:
                        print(f"[WARNING] Found {len(unspecified)} records with 'unspecified' in productionGroup")
                        print("   These need to be cleaned!")
                        print()

                # Check price areas
                if 'priceArea' in df.columns:
                    areas = df['priceArea'].unique()
                    print(f"Price Areas: {sorted(areas.tolist())}")
                    print()

                # Save to CSV and JSON
                print("Saving data...")
                df.to_csv('data/production_2021_from_api.csv', index=False)
                print("[OK] Saved to: data/production_2021_from_api.csv")

                # Also save raw JSON for reference
                with open('data/production_2021_api_response.json', 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                print("[OK] Saved API response to: data/production_2021_api_response.json")
                print()

                return df

            else:
                print("[ERROR] No production data found in API response")
                print("[INFO] The API returned price areas but all had empty data")
                return None
        else:
            print("[ERROR] No data found in API response")
            print(f"Response keys: {data.keys()}")
            return None

    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out after 120 seconds")
        print("   The Elhub API might be slow or unavailable")
        return None

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch data from API")
        print(f"   {type(e).__name__}: {e}")
        return None

    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse JSON response")
        print(f"   {e}")
        return None


def clean_production_labels(df):
    """
    Clean production group labels to remove 'unspecified' suffix.

    Fixes instructor feedback:
    "All production group have an extra «unspecified» part in their labels."
    """

    if df is None or df.empty:
        return df

    print("="*70)
    print("CLEANING PRODUCTION LABELS")
    print("="*70)
    print()

    if 'productionGroup' in df.columns:
        print("Before cleaning:")
        print(f"  Unique groups: {df['productionGroup'].unique().tolist()}")
        print()

        # Remove " - unspecified" and variants
        df['productionGroup'] = df['productionGroup'].str.replace(r'\s*-\s*unspecified', '', regex=True, flags=re.IGNORECASE)
        df['productionGroup'] = df['productionGroup'].str.strip()

        print("After cleaning:")
        print(f"  Unique groups: {df['productionGroup'].unique().tolist()}")
        print()
        print("[OK] Labels cleaned successfully")
    else:
        print("[WARNING] 'productionGroup' column not found")

    return df


if __name__ == "__main__":
    import re

    # Fetch data
    df = fetch_elhub_2021_production()

    if df is not None and not df.empty:
        # Clean labels
        df = clean_production_labels(df)

        # Save cleaned version
        df.to_csv('data/production_2021_cleaned.csv', index=False)
        print()
        print("[OK] Saved cleaned data to: data/production_2021_cleaned.csv")
        print()

        print("="*70)
        print("SUMMARY")
        print("="*70)
        print(f"Total records: {len(df):,}")
        print(f"Date range: {df['startTime'].min()} to {df['startTime'].max()}")
        print(f"Price areas: {len(df['priceArea'].unique())}")
        print(f"Production groups: {len(df['productionGroup'].unique())}")
        print()
        print("[SUCCESS] Real Elhub API data fetched and cleaned!")
        print("   Ready for Cassandra/Spark processing")

    else:
        print()
        print("="*70)
        print("FAILED")
        print("="*70)
        print("[ERROR] Could not fetch data from Elhub API")
        print()
        print("Possible reasons:")
        print("  1. API endpoint changed")
        print("  2. Network connectivity issues")
        print("  3. API temporarily unavailable")
        print("  4. Rate limiting")
        print()
        print("Check the API documentation:")
        print("  https://api.elhub.no/energy-data-api")
