"""
Upload synthetic energy data to MongoDB for Assessment 4
"""

import json
import os
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection (using credentials from Assignment 2)
# NOTE: In production, use environment variables or Streamlit secrets
MONGO_URI = "mongodb+srv://ismasohail_user:IsmaMinhas@cluster0.e3wct64.mongodb.net/ind320?retryWrites=true&w=majority&appName=Cluster0"


def upload_to_mongodb(json_file, collection_name, batch_size=10000):
    """Upload JSON data to MongoDB collection in batches"""

    print(f"\nUploading {json_file} to collection '{collection_name}'...")

    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client["ind320"]
    collection = db[collection_name]

    # Load JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)

    print(f"  Loaded {len(data)} records from file")

    # Convert startTime strings to datetime objects
    for record in data:
        if 'startTime' in record and isinstance(record['startTime'], str):
            record['startTime'] = datetime.fromisoformat(record['startTime'])

    # Clear existing data in collection
    print(f"  Clearing existing data in '{collection_name}'...")
    result = collection.delete_many({})
    print(f"  Deleted {result.deleted_count} existing records")

    # Upload in batches
    print(f"  Uploading in batches of {batch_size}...")
    total_inserted = 0

    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        collection.insert_many(batch)
        total_inserted += len(batch)
        print(f"    Inserted {total_inserted}/{len(data)} records ({100*total_inserted/len(data):.1f}%)")

    print(f"  [OK] Successfully uploaded {total_inserted} records to '{collection_name}'")

    # Create index on startTime for better query performance
    collection.create_index([("startTime", 1)])
    collection.create_index([("priceArea", 1)])

    if "productionGroup" in data[0]:
        collection.create_index([("productionGroup", 1)])
    if "consumptionGroup" in data[0]:
        collection.create_index([("consumptionGroup", 1)])

    print(f"  [OK] Created indexes for faster queries")

    client.close()


def verify_upload(collection_name):
    """Verify data was uploaded correctly"""
    client = MongoClient(MONGO_URI)
    db = client["ind320"]
    collection = db[collection_name]

    count = collection.count_documents({})
    print(f"\n  Verification: {collection_name} contains {count:,} records")

    # Show sample record
    sample = collection.find_one()
    if sample:
        print(f"  Sample record: {sample}")

    client.close()


if __name__ == "__main__":
    print("=" * 70)
    print("UPLOADING SYNTHETIC DATA TO MONGODB")
    print("=" * 70)

    # Check if data files exist
    data_files = [
        ("data/production_2021.json", "elhub_production_2021"),
        ("data/consumption_2021.json", "elhub_consumption_2021"),
        ("data/production_2022_2024.json", "elhub_production_2022_2024"),
        ("data/consumption_2022_2024.json", "elhub_consumption_2022_2024"),
    ]

    for json_file, collection_name in data_files:
        if not os.path.exists(json_file):
            print(f"\n[WARNING] {json_file} not found. Run generate_synthetic_data.py first.")
            continue

        try:
            upload_to_mongodb(json_file, collection_name)
            verify_upload(collection_name)
        except Exception as e:
            print(f"\n[ERROR] Error uploading {json_file}: {e}")

    print("\n" + "=" * 70)
    print("MONGODB UPLOAD COMPLETE!")
    print("=" * 70)
    print("\nCollections created:")
    print("  - elhub_production_2021")
    print("  - elhub_consumption_2021")
    print("  - elhub_production_2022_2024")
    print("  - elhub_consumption_2022_2024")
    print("\nData is ready for Assessment 4 Streamlit app!")
