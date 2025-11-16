"""
Generate synthetic energy production and consumption data for Assessment 4
Mimics real Elhub data structure with realistic patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Set random seed for reproducibility
np.random.seed(42)

# Configuration
PRICE_AREAS = ["NO1", "NO2", "NO3", "NO4", "NO5"]
PRODUCTION_GROUPS = ["Hydro", "Wind", "Thermal", "Solar"]
CONSUMPTION_GROUPS = ["Residential", "Commercial", "Industrial", "Other"]


def generate_hourly_timestamps(start_year, end_year):
    """Generate hourly timestamps for given year range"""
    start_date = datetime(start_year, 1, 1, 0, 0, 0)
    end_date = datetime(end_year, 12, 31, 23, 0, 0)

    timestamps = []
    current = start_date
    while current <= end_date:
        timestamps.append(current)
        current += timedelta(hours=1)

    return timestamps


def get_production_baseline(area, group):
    """Get baseline production values by area and group (MWh)"""
    baselines = {
        "NO1": {"Hydro": 1200, "Wind": 400, "Thermal": 300, "Solar": 50},
        "NO2": {"Hydro": 800, "Wind": 350, "Thermal": 250, "Solar": 40},
        "NO3": {"Hydro": 1500, "Wind": 500, "Thermal": 200, "Solar": 30},
        "NO4": {"Hydro": 600, "Wind": 800, "Thermal": 150, "Solar": 20},
        "NO5": {"Hydro": 1000, "Wind": 600, "Thermal": 280, "Solar": 35},
    }
    return baselines[area][group]


def get_consumption_baseline(area, group):
    """Get baseline consumption values by area and group (MWh)"""
    baselines = {
        "NO1": {"Residential": 800, "Commercial": 600, "Industrial": 1200, "Other": 200},
        "NO2": {"Residential": 600, "Commercial": 450, "Industrial": 900, "Other": 150},
        "NO3": {"Residential": 500, "Commercial": 400, "Industrial": 800, "Other": 120},
        "NO4": {"Residential": 300, "Commercial": 250, "Industrial": 500, "Other": 80},
        "NO5": {"Residential": 700, "Commercial": 550, "Industrial": 1000, "Other": 180},
    }
    return baselines[area][group]


def add_seasonal_variation(values, timestamps, group):
    """Add realistic seasonal patterns"""
    seasonal_factors = []

    for ts in timestamps:
        month = ts.month

        # Different patterns for different groups
        if group in ["Hydro", "Residential"]:
            # Higher in winter, lower in summer
            if month in [12, 1, 2]:
                factor = 1.4
            elif month in [6, 7, 8]:
                factor = 0.7
            else:
                factor = 1.0
        elif group in ["Wind"]:
            # Higher in winter, moderate in summer
            if month in [11, 12, 1, 2, 3]:
                factor = 1.3
            elif month in [6, 7, 8]:
                factor = 0.9
            else:
                factor = 1.0
        elif group == "Solar":
            # Higher in summer, very low in winter
            if month in [5, 6, 7, 8]:
                factor = 2.0
            elif month in [11, 12, 1, 2]:
                factor = 0.3
            else:
                factor = 1.0
        elif group in ["Commercial", "Industrial"]:
            # Relatively stable year-round
            factor = 1.0 + 0.1 * np.sin((month - 1) * np.pi / 6)
        else:
            factor = 1.0

        seasonal_factors.append(factor)

    return values * np.array(seasonal_factors)


def add_daily_variation(values, timestamps, group):
    """Add realistic daily (hourly) patterns"""
    daily_factors = []

    for ts in timestamps:
        hour = ts.hour

        if group in ["Solar"]:
            # Solar only during daylight hours
            if 6 <= hour <= 18:
                factor = 1.5 * np.sin((hour - 6) * np.pi / 12)
            else:
                factor = 0.0
        elif group in ["Residential"]:
            # Peak in morning and evening
            if hour in [7, 8, 9, 18, 19, 20]:
                factor = 1.3
            elif hour in [0, 1, 2, 3, 4, 5]:
                factor = 0.6
            else:
                factor = 1.0
        elif group in ["Commercial"]:
            # Peak during business hours
            if 8 <= hour <= 18:
                factor = 1.4
            else:
                factor = 0.6
        elif group in ["Industrial"]:
            # More stable, slightly lower at night
            if 0 <= hour <= 6:
                factor = 0.9
            else:
                factor = 1.0
        else:
            # Production groups - relatively stable
            factor = 1.0 + 0.1 * np.random.randn()

        daily_factors.append(max(0, factor))

    return values * np.array(daily_factors)


def add_weekly_variation(values, timestamps, group):
    """Add weekly patterns (weekday vs weekend)"""
    weekly_factors = []

    for ts in timestamps:
        weekday = ts.weekday()  # 0=Monday, 6=Sunday

        if group in ["Commercial", "Industrial"]:
            # Lower on weekends
            if weekday >= 5:  # Saturday, Sunday
                factor = 0.7
            else:
                factor = 1.0
        else:
            factor = 1.0

        weekly_factors.append(factor)

    return values * np.array(weekly_factors)


def add_noise(values, noise_level=0.15):
    """Add random noise to make data realistic"""
    noise = np.random.normal(0, noise_level, len(values))
    return values * (1 + noise)


def generate_production_data(start_year, end_year):
    """Generate synthetic production data for given year range"""
    timestamps = generate_hourly_timestamps(start_year, end_year)
    records = []

    print(f"Generating production data for {start_year}-{end_year}...")

    for area in PRICE_AREAS:
        for group in PRODUCTION_GROUPS:
            print(f"  Processing {area} - {group}")

            # Get baseline value
            baseline = get_production_baseline(area, group)

            # Start with baseline for all timestamps
            values = np.full(len(timestamps), baseline, dtype=float)

            # Add realistic variations
            values = add_seasonal_variation(values, timestamps, group)
            values = add_daily_variation(values, timestamps, group)
            values = add_noise(values, noise_level=0.12)

            # Ensure non-negative
            values = np.maximum(values, 0)

            # Create records
            for i, ts in enumerate(timestamps):
                records.append({
                    "priceArea": area,
                    "productionGroup": group,
                    "startTime": ts,
                    "quantityMWh": round(values[i], 2)
                })

    df = pd.DataFrame(records)
    print(f"Generated {len(df)} production records")
    return df


def generate_consumption_data(start_year, end_year):
    """Generate synthetic consumption data for given year range"""
    timestamps = generate_hourly_timestamps(start_year, end_year)
    records = []

    print(f"Generating consumption data for {start_year}-{end_year}...")

    for area in PRICE_AREAS:
        for group in CONSUMPTION_GROUPS:
            print(f"  Processing {area} - {group}")

            # Get baseline value
            baseline = get_consumption_baseline(area, group)

            # Start with baseline for all timestamps
            values = np.full(len(timestamps), baseline, dtype=float)

            # Add realistic variations
            values = add_seasonal_variation(values, timestamps, group)
            values = add_daily_variation(values, timestamps, group)
            values = add_weekly_variation(values, timestamps, group)
            values = add_noise(values, noise_level=0.15)

            # Ensure non-negative
            values = np.maximum(values, 0)

            # Create records
            for i, ts in enumerate(timestamps):
                records.append({
                    "priceArea": area,
                    "consumptionGroup": group,
                    "startTime": ts,
                    "quantityMWh": round(values[i], 2)
                })

    df = pd.DataFrame(records)
    print(f"Generated {len(df)} consumption records")
    return df


def save_to_csv(df, filename):
    """Save dataframe to CSV"""
    df.to_csv(filename, index=False)
    print(f"Saved to {filename}")


def save_to_mongodb_format(df, filename):
    """Save dataframe in MongoDB-ready JSON format"""
    # Convert timestamps to ISO format strings for MongoDB
    df_copy = df.copy()
    df_copy['startTime'] = df_copy['startTime'].dt.strftime('%Y-%m-%dT%H:%M:%S')

    records = df_copy.to_dict('records')

    with open(filename, 'w') as f:
        json.dump(records, f, indent=2)

    print(f"Saved to {filename}")


if __name__ == "__main__":
    import os

    # Create data directory
    os.makedirs("data", exist_ok=True)

    print("=" * 60)
    print("GENERATING SYNTHETIC ENERGY DATA FOR ASSESSMENT 4")
    print("=" * 60)

    # Generate 2021 consumption data
    print("\n1. Generating 2021 consumption data...")
    df_cons_2021 = generate_consumption_data(2021, 2021)
    save_to_csv(df_cons_2021, "data/consumption_2021.csv")
    save_to_mongodb_format(df_cons_2021, "data/consumption_2021.json")

    # Generate 2022-2024 production data
    print("\n2. Generating 2022-2024 production data...")
    df_prod_2022_2024 = generate_production_data(2022, 2024)
    save_to_csv(df_prod_2022_2024, "data/production_2022_2024.csv")
    save_to_mongodb_format(df_prod_2022_2024, "data/production_2022_2024.json")

    # Generate 2022-2024 consumption data
    print("\n3. Generating 2022-2024 consumption data...")
    df_cons_2022_2024 = generate_consumption_data(2022, 2024)
    save_to_csv(df_cons_2022_2024, "data/consumption_2022_2024.csv")
    save_to_mongodb_format(df_cons_2022_2024, "data/consumption_2022_2024.json")

    # Also generate 2021 production for completeness (already exists but ensure consistency)
    print("\n4. Generating 2021 production data (for completeness)...")
    df_prod_2021 = generate_production_data(2021, 2021)
    save_to_csv(df_prod_2021, "data/production_2021.csv")
    save_to_mongodb_format(df_prod_2021, "data/production_2021.json")

    print("\n" + "=" * 60)
    print("DATA GENERATION COMPLETE!")
    print("=" * 60)
    print(f"\nSummary:")
    print(f"  2021 Production:     {len(df_prod_2021):,} records")
    print(f"  2021 Consumption:    {len(df_cons_2021):,} records")
    print(f"  2022-2024 Production: {len(df_prod_2022_2024):,} records")
    print(f"  2022-2024 Consumption: {len(df_cons_2022_2024):,} records")
    print(f"\nTotal records: {len(df_prod_2021) + len(df_cons_2021) + len(df_prod_2022_2024) + len(df_cons_2022_2024):,}")
    print("\nFiles saved in 'data/' directory")
