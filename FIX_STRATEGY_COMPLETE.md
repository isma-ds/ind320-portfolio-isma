# Complete Fix Strategy for Assessment 2 & 3

## FOUND PROBLEMS IN CURRENT CODE

### Critical Issues in `assignment3_update` Branch:

1. **app.py Line 64:** `prod = pd.read_csv("data/production_per_group_mba_hour.csv")` ❌
   - Using CSV download instead of MongoDB

2. **pages/02_PriceArea.py Lines 41-52:** `load_elhub_demo()` generates FAKE data ❌
   - Not using real Elhub API
   - Not using MongoDB

3. **STL Plot:** Single plot instead of 4 separate components ❌

4. **No MongoDB connection** anywhere in Streamlit ❌

5. **Multiple navigation menus** (in app.py AND pages) ❌

---

## FIX PLAN - STEP BY STEP

### Phase 1: Setup (15 minutes)

#### Step 1: Stay on assignment3_update branch
```bash
# Already on assignment3_update
git status

# Create backup just in case
git branch assignment3_backup
```

#### Step 2: Copy working files from assessment4
We have proven working solutions! Copy these:
- `cassandra_client.py` (MongoDB connection)
- `docker-compose.yml` (Cassandra setup)
- `scripts/fetch_elhub_data.py` (Real API)
- `.streamlit/secrets.toml` (MongoDB credentials)

```bash
# Copy from assessment4 branch
git checkout assessment4 -- cassandra_client.py
git checkout assessment4 -- docker-compose.yml
git checkout assessment4 -- scripts/fetch_elhub_data.py
git checkout assessment4 -- .streamlit/secrets.toml
```

---

### Phase 2: Fix Jupyter Notebook (1 hour)

#### Open `notebooks/IND320_Assignment3.ipynb`

Need to add/fix Assessment 2 requirements that are missing:

**NEW CELL 1: Fetch 2021 Data from Real Elhub API**
```python
import requests
import pandas as pd

# ✅ CORRECT API USAGE (not CSV download!)
url = "https://api.elhub.no/energy-data/v0/price-areas"
params = {
    "dataset": "PRODUCTION_PER_GROUP_MBA_HOUR",
    "startTime": "2021-01-01T00:00:00Z",
    "endTime": "2021-12-31T23:59:59Z"
}

print("Fetching 2021 production data from Elhub API...")
response = requests.get(url, params=params, timeout=60)
response.raise_for_status()

data = response.json()

# Extract productionPerGroupMbaHour from JSON
production_list = data['data'][0]['attributes']['productionPerGroupMbaHour']

# Convert to DataFrame
df_2021 = pd.DataFrame(production_list)

print(f"✅ Fetched {len(df_2021)} records via API (NO CSV!)")
print(df_2021.head())
print(df_2021.columns.tolist())
```

**NEW CELL 2: Insert to Cassandra via Spark**
```python
from pyspark.sql import SparkSession

# Start Spark with Cassandra connector
spark = SparkSession.builder \
    .appName("IND320_Assignment3_Cassandra") \
    .config("spark.jars.packages", "com.datastax.spark:spark-cassandra-connector_2.12:3.4.0") \
    .config("spark.cassandra.connection.host", "127.0.0.1") \
    .config("spark.cassandra.connection.port", "9042") \
    .getOrCreate()

# Convert Pandas to Spark DataFrame
df_spark = spark.createDataFrame(df_2021)

# Write to Cassandra
df_spark.write \
    .format("org.apache.spark.sql.cassandra") \
    .mode("append") \
    .option("keyspace", "ind320") \
    .option("table", "production_2021") \
    .save()

print(f"✅ Inserted {df_spark.count()} rows to Cassandra")
```

**NEW CELL 3: Extract 4 Columns from Cassandra using Spark**
```python
# Read from Cassandra
df_cassandra = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .option("keyspace", "ind320") \
    .option("table", "production_2021") \
    .load()

# Select ONLY 4 required columns
df_filtered = df_cassandra.select(
    "priceArea",
    "productionGroup",
    "startTime",
    "quantityKwh"
)

# Convert to Pandas
df_final = df_filtered.toPandas()

print(f"✅ Extracted {len(df_final)} rows with 4 columns")
print(df_final.head())
print(df_final['productionGroup'].unique())  # Check for "unspecified"
```

**NEW CELL 4: Clean Labels (Remove "unspecified")**
```python
# Fix the "unspecified" issue the instructor mentioned
df_final['productionGroup'] = df_final['productionGroup'].str.replace(' - unspecified', '', regex=False)
df_final['productionGroup'] = df_final['productionGroup'].str.replace('- unspecified', '', regex=False)
df_final['productionGroup'] = df_final['productionGroup'].str.strip()

print("✅ Cleaned production group labels")
print(df_final['productionGroup'].unique())
# Should be: ['Hydro', 'Wind', 'Thermal', 'Solar'] with NO "unspecified"
```

**NEW CELL 5: Create Pie Chart (Assessment 2 Requirement)**
```python
import matplotlib.pyplot as plt

# Choose NO1 price area
price_area = "NO1"
df_area = df_final[df_final['priceArea'] == price_area]

# Group by production group and sum
total_by_group = df_area.groupby('productionGroup')['quantityKwh'].sum()

# Pie chart
plt.figure(figsize=(8, 8))
plt.pie(
    total_by_group.values,
    labels=total_by_group.index,
    autopct='%1.1f%%',
    startangle=90
)
plt.title(f'Total Production 2021 - {price_area}')
plt.axis('equal')
plt.show()

print(f"✅ Pie chart for {price_area}")
```

**NEW CELL 6: Create Line Plot for First Month (Assessment 2 Requirement)**
```python
# Convert startTime to datetime
df_final['startTime'] = pd.to_datetime(df_final['startTime'])

# Filter for January 2021 (first month) and NO1
df_jan = df_final[
    (df_final['priceArea'] == price_area) &
    (df_final['startTime'].dt.month == 1)
]

# Create line plot
plt.figure(figsize=(14, 6))

for group in df_jan['productionGroup'].unique():
    df_group = df_jan[df_jan['productionGroup'] == group]
    plt.plot(df_group['startTime'], df_group['quantityKwh'], label=group, linewidth=1.5)

plt.xlabel('Time')
plt.ylabel('Production (kWh)')
plt.title(f'Hourly Production - January 2021 - {price_area}')
plt.legend()
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

print(f"✅ Line plot for January 2021, {price_area}")
```

**NEW CELL 7: Insert to MongoDB**
```python
from pymongo import MongoClient

# Connect to MongoDB
mongo_uri = "mongodb+srv://ismasohail_user:IsmaMinhas@cluster0.e3wct64.mongodb.net/ind320?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri)

db = client['ind320']
collection = db['production_2021']

# Drop existing collection to avoid duplicates
collection.drop()

# Convert DataFrame to records
records = df_final.to_dict('records')

# Insert to MongoDB
result = collection.insert_many(records)

print(f"✅ Inserted {len(result.inserted_ids)} records to MongoDB")
print(f"Collection: ind320.production_2021")

# Verify
count = collection.count_documents({})
print(f"Total documents in MongoDB: {count}")

client.close()
```

---

### Phase 3: Fix STL to 4 Separate Plots (30 minutes)

#### Update `notebooks/utils_analysis.py`

Find the `stl_production_plot()` function and replace it:

```python
def stl_production_plot(df, area="NO5", group="Hydro"):
    """
    Create STL decomposition with 4 SEPARATE plots (not 1 combined plot).

    Fixed based on instructor feedback: Must show 4 components separately.
    """
    from statsmodels.tsa.seasonal import STL
    import matplotlib.pyplot as plt

    # Filter data
    df_filtered = df[
        (df['priceArea'] == area) &
        (df['productionGroup'] == group)
    ].copy()

    df_filtered['startTime'] = pd.to_datetime(df_filtered['startTime'])
    df_filtered = df_filtered.set_index('startTime').sort_index()

    # Ensure regular frequency
    df_filtered = df_filtered.resample('H').mean()
    series = df_filtered['quantityKwh'].fillna(method='ffill')

    # Perform STL decomposition
    stl = STL(series, period=24*7)  # Weekly seasonality
    result = stl.fit()

    # Create 4 SEPARATE subplots
    fig, axes = plt.subplots(4, 1, figsize=(14, 10))

    # Plot 1: Original data
    axes[0].plot(result.observed, label='Original', color='black', linewidth=0.8)
    axes[0].set_ylabel('Original')
    axes[0].set_title(f'STL Decomposition - {area} - {group}')
    axes[0].legend(loc='upper right')
    axes[0].grid(True, alpha=0.3)

    # Plot 2: Trend
    axes[1].plot(result.trend, label='Trend', color='blue', linewidth=1.5)
    axes[1].set_ylabel('Trend')
    axes[1].legend(loc='upper right')
    axes[1].grid(True, alpha=0.3)

    # Plot 3: Seasonal
    axes[2].plot(result.seasonal, label='Seasonal', color='green', linewidth=0.8)
    axes[2].set_ylabel('Seasonal')
    axes[2].legend(loc='upper right')
    axes[2].grid(True, alpha=0.3)

    # Plot 4: Residual
    axes[3].plot(result.resid, label='Residual', color='red', linewidth=0.5)
    axes[3].set_ylabel('Residual')
    axes[3].set_xlabel('Time')
    axes[3].legend(loc='upper right')
    axes[3].grid(True, alpha=0.3)

    plt.tight_layout()
    return fig
```

---

### Phase 4: Fix Streamlit Pages (1.5 hours)

#### Fix 1: Connect ALL Pages to MongoDB (No CSV!)

Create `lib/mongodb_client.py`:

```python
"""
MongoDB client for Streamlit pages.
Replaces all CSV downloads with MongoDB queries.
"""

import streamlit as st
from pymongo import MongoClient
import pandas as pd

@st.cache_resource
def get_mongo_client():
    """Get cached MongoDB client."""
    try:
        mongo_uri = st.secrets["MONGO_URI"]
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        return client
    except Exception as e:
        st.error(f"MongoDB connection failed: {e}")
        return None

@st.cache_data(ttl=3600)
def load_production_2021():
    """
    Load 2021 production data from MongoDB.
    NO CSV DOWNLOADS!
    """
    client = get_mongo_client()
    if not client:
        return pd.DataFrame()

    db = client['ind320']
    collection = db['production_2021']

    # Query all records
    cursor = collection.find({}, {'_id': 0})
    df = pd.DataFrame(list(cursor))

    # Convert timestamps
    if 'startTime' in df.columns:
        df['startTime'] = pd.to_datetime(df['startTime'])

    return df
```

#### Fix 2: Update app.py (Remove CSV, Add MongoDB)

Replace line 64 in app.py:

```python
# OLD (WRONG):
# prod = pd.read_csv("data/production_per_group_mba_hour.csv")

# NEW (CORRECT):
from lib.mongodb_client import load_production_2021
prod = load_production_2021()

if prod.empty:
    st.error("Failed to load production data from MongoDB")
    st.stop()
```

#### Fix 3: Update pages/02_PriceArea.py

Replace the fake `load_elhub_demo()` function:

```python
# OLD (WRONG - lines 41-52):
# @st.cache_data
# def load_elhub_demo():
#     df = pd.DataFrame({...})  # FAKE DATA
#     return df

# NEW (CORRECT):
from lib.mongodb_client import load_production_2021

@st.cache_data(ttl=3600)
def load_real_production():
    """Load real 2021 production data from MongoDB."""
    df = load_production_2021()
    if df.empty:
        st.error("No data available from MongoDB")
        return pd.DataFrame()

    # Aggregate by month for visualization
    df['startTime'] = pd.to_datetime(df['startTime'])
    df['month'] = df['startTime'].dt.month

    monthly = df.groupby(['priceArea', 'month', 'productionGroup'])['quantityKwh'].sum().reset_index()
    return monthly

# Use it:
elhub_df = load_real_production()
```

#### Fix 4: Add Page 2 (LineChartColumn) if missing

Create `pages/08_Assessment1_Page2.py`:

```python
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Data Table", layout="wide")
st.title("📊 Data Table with Line Charts")

# Load open-meteo data (from Assessment 1)
@st.cache_data
def load_meteo_data():
    df = pd.read_csv("data/open-meteo-subset.csv", parse_dates=['time'])
    return df

df = load_meteo_data()

st.subheader("First Month Data with LineChartColumn")

# Filter to first month
df_first_month = df[df['time'].dt.month == 1]

# Show each column with line chart
columns = [col for col in df.columns if col != 'time']

for col in columns:
    st.write(f"**{col}**")

    # Create DataFrame with time and this column
    df_chart = df_first_month[['time', col]].set_index('time')

    # Use line_chart (this is the LineChartColumn equivalent)
    st.line_chart(df_chart)

    st.markdown("---")
```

#### Fix 5: Add Page 3 with Month Selector Slider (not "days back")

Create or update to use proper month selector:

```python
# In page 03 or 05:
st.subheader("Select Month Range")

# Use st.select_slider for months
months = list(range(1, 13))
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

selected_months = st.select_slider(
    "Select month range:",
    options=months,
    value=(1, 1),  # Default: first month
    format_func=lambda x: month_names[x-1]
)

st.write(f"Selected: {month_names[selected_months[0]-1]} to {month_names[selected_months[1]-1]}")
```

---

### Phase 5: Fix Assessment 3 Specific Issues (45 minutes)

#### Fix 1: Move LOF to Tab

In the page with SPC + LOF:

```python
# Create tabs
tab1, tab2 = st.tabs(["📊 SPC Analysis", "🔍 LOF Analysis"])

with tab1:
    st.subheader("SPC Analysis with DCT")
    # ... SPC code here ...

with tab2:
    st.subheader("LOF (Local Outlier Factor) Analysis")
    # ... LOF code here ...
```

#### Fix 2: Add Curved Control Limits to SPC

```python
def spc_with_curved_limits(data, window_size=24):
    """
    SPC analysis with HIGH-PASS FILTERING for curved control limits.
    """
    from scipy import signal

    # High-pass filter
    sos = signal.butter(4, 0.1, 'highpass', output='sos')
    data_filtered = signal.sosfilt(sos, data)

    # Calculate control limits on FILTERED data
    mean = np.mean(data_filtered)
    std = np.std(data_filtered)

    ucl = mean + 3 * std
    lcl = mean - 3 * std

    # These will be CURVED when plotted against original data
    return data_filtered, ucl, lcl
```

#### Fix 3: Remove Duplicate Menu

In `app.py`, remove the radio button navigation if pages already have sidebar navigation automatically.

---

### Phase 6: Final Checks (30 minutes)

#### Checklist:

- [ ] No CSV downloads anywhere (search for `.csv` in all .py files)
- [ ] All Streamlit pages use MongoDB via `lib/mongodb_client.py`
- [ ] `.streamlit/secrets.toml` exists with MongoDB URI
- [ ] Jupyter notebook has complete workflow: API → Cassandra → Spark → MongoDB
- [ ] STL plot shows 4 separate subplots
- [ ] SPC has curved control limits
- [ ] LOF is in a tab
- [ ] Page 2 has LineChartColumn equivalent
- [ ] Page 3 has month selector slider
- [ ] Page 4 labels are clean (no "unspecified")
- [ ] Single navigation menu (not duplicate)

#### Test Locally:

```bash
venv\Scripts\streamlit.exe run app.py
```

Check EVERY page works with MongoDB.

---

### Phase 7: Deploy (30 minutes)

#### Step 1: Commit Changes

```bash
git add .
git commit -m "Fix all Assessment 2 and 3 issues based on instructor feedback:
- Replace CSV downloads with real Elhub API
- Connect Streamlit to MongoDB (no CSV in app)
- Add Cassandra-Spark workflow to notebook
- Fix STL to 4 separate plots
- Add curved control limits to SPC
- Move LOF to tab
- Fix Page 2, 3, 4 issues
- Clean production labels (remove unspecified)
- Remove duplicate navigation"

git push origin assignment3_update
```

#### Step 2: Merge to Main

```bash
git checkout main
git merge assignment3_update
git push origin main
```

#### Step 3: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io
2. Delete old app if exists
3. Create new app:
   - Repository: ind320-portfolio-isma
   - Branch: **main**
   - Main file: app.py
4. Add secrets: `MONGO_URI = "..."`
5. Make app **PUBLIC**
6. Test from logged-out browser

#### Step 4: Verify Public Access

```bash
# Test URL from incognito/private browser
# Should work WITHOUT login
```

---

## TIME ESTIMATE

**Total: 4-5 hours**

- Phase 1: Setup (15 min)
- Phase 2: Jupyter Notebook (60 min)
- Phase 3: STL Fix (30 min)
- Phase 4: Streamlit MongoDB (90 min)
- Phase 5: Assessment 3 Fixes (45 min)
- Phase 6: Testing (30 min)
- Phase 7: Deploy (30 min)

---

## CRITICAL SUCCESS CRITERIA

✅ **MUST HAVE:**
1. Real Elhub API in Jupyter (no CSV download)
2. MongoDB in ALL Streamlit pages (no CSV)
3. App is PUBLIC and accessible
4. Cassandra working (Docker is fine)
5. 4 columns extracted via Spark
6. STL: 4 separate plots
7. Clean labels (no "unspecified")
8. Merged to main branch

✅ **SHOULD HAVE:**
9. SPC curved limits
10. LOF in tab
11. Page 2 LineChartColumn
12. Page 3 month slider

---

**Ready to start fixing? Let me know and I'll guide you through each phase!**
