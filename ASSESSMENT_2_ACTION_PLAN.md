# Assessment 2 - Action Plan to Complete ASAP

## Current Situation Analysis

### What You Have Now:
- ✅ On `assessment4` branch (completed, but need to go back)
- ✅ `origin/assignment2` branch exists with some work
- ✅ MongoDB Atlas account setup
- ✅ MongoDB connection working
- ✅ Virtual environment with all packages
- ✅ Elhub API fetcher created (in assessment4)

### What's Missing for Assessment 2:
- ❌ Cassandra + Spark setup (local)
- ❌ 2021 production data workflow (API → Cassandra → Spark → MongoDB)
- ❌ Specific plots (pie chart, line plot)
- ❌ Streamlit Page 4 with required layout
- ❌ Jupyter Notebook for Assessment 2 properly completed

---

## FAST TRACK PLAN (Estimated: 3-4 hours)

### Phase 1: Setup Branch (10 minutes)

#### Option A: Start Fresh Assignment 2 Branch
```bash
cd "C:\Users\hisha\Documents\Aoun Assignment\ind320-portfolio-isma"

# Checkout existing assignment2 work
git checkout -b assignment2_final origin/assignment2

# Or if you want to start from main
git checkout main
git checkout -b assignment2_final
```

#### Option B: Check What's Already There
```bash
# Download and check existing assignment2 branch
git checkout assignment2
git pull origin assignment2

# See what files exist
ls notebooks/
ls pages/
```

**DECISION POINT:** Check if `notebooks/IND320_Part2.ipynb` exists and has the required work. If yes, skip to Phase 3. If no, continue to Phase 2.

---

### Phase 2: Complete Jupyter Notebook (2 hours)

This is the CORE requirement. You need proper data flow:

#### Step 1: Install Cassandra + Spark (30 min)

**QUICK OPTION - Use Docker (Recommended):**
```bash
# You already have docker-compose.yml for Cassandra from assessment4
# Copy it to use for assignment2
cd "C:\Users\hisha\Documents\Aoun Assignment\ind320-portfolio-isma"
git checkout assessment4 -- docker-compose.yml cassandra-init/

# Start Cassandra
cassandra_manager.bat start
```

**Install PySpark:**
```bash
venv\Scripts\pip.exe install pyspark
```

#### Step 2: Fetch 2021 Production Data (15 min)

Create: `scripts/fetch_2021_production.py`

```python
import requests
import pandas as pd
from datetime import datetime

# Elhub API endpoint
url = "https://api.elhub.no/energy-data/v0/price-areas"
params = {
    "dataset": "PRODUCTION_PER_GROUP_MBA_HOUR",
    "startTime": "2021-01-01T00:00:00Z",
    "endTime": "2021-12-31T23:59:59Z"
}

response = requests.get(url, params=params)
data = response.json()

# Extract productionPerGroupMbaHour
production_list = data['data'][0]['attributes']['productionPerGroupMbaHour']

# Convert to DataFrame
df = pd.DataFrame(production_list)

# Save to CSV (for reference)
df.to_csv('data/production_2021.csv', index=False)

print(f"Fetched {len(df)} records for 2021 production data")
print(df.head())
```

Run it:
```bash
venv\Scripts\python.exe scripts/fetch_2021_production.py
```

#### Step 3: Cassandra + Spark Workflow (45 min)

Create Jupyter Notebook: `notebooks/IND320_Assignment2.ipynb`

**Cell 1: Setup**
```python
from pyspark.sql import SparkSession
from cassandra.cluster import Cluster
import pandas as pd

# Create Spark session with Cassandra connector
spark = SparkSession.builder \
    .appName("IND320_Assignment2") \
    .config("spark.cassandra.connection.host", "127.0.0.1") \
    .config("spark.cassandra.connection.port", "9042") \
    .getOrCreate()
```

**Cell 2: Load Data to Cassandra**
```python
# Read production data
df_pandas = pd.read_csv('data/production_2021.csv')

# Convert to Spark DataFrame
df_spark = spark.createDataFrame(df_pandas)

# Write to Cassandra
df_spark.write \
    .format("org.apache.spark.sql.cassandra") \
    .mode("append") \
    .option("keyspace", "ind320") \
    .option("table", "production_2021") \
    .save()

print(f"Inserted {df_spark.count()} rows into Cassandra")
```

**Cell 3: Extract 4 Columns from Cassandra using Spark**
```python
# Read from Cassandra
df_cassandra = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .option("keyspace", "ind320") \
    .option("table", "production_2021") \
    .load()

# Select only required columns
df_filtered = df_cassandra.select(
    "priceArea",
    "productionGroup",
    "startTime",
    "quantityKwh"
)

# Convert to Pandas for easier manipulation
df_final = df_filtered.toPandas()

print(f"Extracted {len(df_final)} rows with 4 columns")
print(df_final.head())
```

**Cell 4: Create Pie Chart**
```python
import matplotlib.pyplot as plt

# Choose a price area (e.g., NO1)
price_area = "NO1"

# Filter and group by production group
df_area = df_final[df_final['priceArea'] == price_area]
total_by_group = df_area.groupby('productionGroup')['quantityKwh'].sum()

# Pie chart
plt.figure(figsize=(8, 8))
plt.pie(total_by_group.values, labels=total_by_group.index, autopct='%1.1f%%')
plt.title(f'Total Production 2021 - {price_area}')
plt.show()
```

**Cell 5: Create Line Plot (First Month)**
```python
import pandas as pd

# Filter for January 2021 and chosen price area
df_area['startTime'] = pd.to_datetime(df_area['startTime'])
df_jan = df_area[df_area['startTime'].dt.month == 1]

# Pivot for line plot
df_pivot = df_jan.pivot_table(
    values='quantityKwh',
    index='startTime',
    columns='productionGroup',
    aggfunc='sum'
)

# Line plot
plt.figure(figsize=(12, 6))
for col in df_pivot.columns:
    plt.plot(df_pivot.index, df_pivot[col], label=col)

plt.xlabel('Time')
plt.ylabel('Production (kWh)')
plt.title(f'Hourly Production - January 2021 - {price_area}')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

**Cell 6: Insert into MongoDB**
```python
from pymongo import MongoClient

# Connect to MongoDB
mongo_uri = "mongodb+srv://ismasohail_user:IsmaMinhas@cluster0.e3wct64.mongodb.net/ind320?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri)
db = client['ind320']
collection = db['production_2021']

# Convert DataFrame to dict and insert
records = df_final.to_dict('records')
collection.insert_many(records)

print(f"Inserted {len(records)} records into MongoDB")
client.close()
```

**Cell 7: AI Usage and Log**
```markdown
## AI Usage

I used Claude Code (Anthropic) to assist with:
- Setting up Spark-Cassandra connection
- Understanding Elhub API structure
- Creating data pipeline from API → Cassandra → Spark → MongoDB
- Debugging PySpark DataFrame operations
- Creating visualization code

## Work Log (300-500 words)

This assignment involved creating a complete data pipeline using multiple technologies...
[Write 300-500 words describing your experience]

## Links

- GitHub Repository: https://github.com/isma-ds/ind320-portfolio-isma
- Branch: assignment2_final
- Streamlit App: https://ind320-portfolio-isma.streamlit.app/
```

#### Step 4: Run All Cells & Export PDF (10 min)

1. Run all cells in order
2. Verify all outputs appear
3. Export to PDF: File → Download as → PDF
4. Save .ipynb to GitHub

---

### Phase 3: Update Streamlit App (1 hour)

#### Step 1: Create Page 4 (30 min)

Create: `pages/04_Production_Analysis.py`

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pymongo import MongoClient

st.set_page_config(page_title="Production Analysis", page_icon="⚡", layout="wide")

st.title("⚡ Production Analysis - 2021")

# MongoDB connection
@st.cache_resource
def get_mongo_client():
    mongo_uri = st.secrets["MONGO_URI"]
    return MongoClient(mongo_uri)

@st.cache_data(ttl=3600)
def load_production_data():
    client = get_mongo_client()
    db = client['ind320']
    collection = db['production_2021']

    df = pd.DataFrame(list(collection.find({}, {'_id': 0})))
    df['startTime'] = pd.to_datetime(df['startTime'])
    return df

# Load data
df = load_production_data()

# Two columns layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Total Production by Group")

    # Radio buttons for price area
    price_area = st.radio(
        "Select Price Area:",
        options=['NO1', 'NO2', 'NO3', 'NO4', 'NO5'],
        horizontal=True
    )

    # Filter and aggregate
    df_area = df[df['priceArea'] == price_area]
    total_by_group = df_area.groupby('productionGroup')['quantityKwh'].sum()

    # Pie chart
    fig_pie = go.Figure(data=[go.Pie(
        labels=total_by_group.index,
        values=total_by_group.values,
        hole=0.3
    )])

    fig_pie.update_layout(
        title=f"Total Production 2021 - {price_area}",
        height=400
    )

    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("Monthly Production Trends")

    # Pills for production groups
    all_groups = df['productionGroup'].unique().tolist()
    selected_groups = st.pills(
        "Select Production Groups:",
        options=all_groups,
        selection_mode="multi",
        default=all_groups
    )

    # Month selector
    month = st.selectbox(
        "Select Month:",
        options=list(range(1, 13)),
        format_func=lambda x: pd.to_datetime(f'2021-{x:02d}-01').strftime('%B')
    )

    # Filter data
    df_filtered = df[
        (df['priceArea'] == price_area) &
        (df['productionGroup'].isin(selected_groups if selected_groups else all_groups)) &
        (df['startTime'].dt.month == month)
    ]

    # Line plot
    fig_line = px.line(
        df_filtered,
        x='startTime',
        y='quantityKwh',
        color='productionGroup',
        title=f"Hourly Production - {pd.to_datetime(f'2021-{month:02d}-01').strftime('%B')} 2021 - {price_area}"
    )

    fig_line.update_layout(
        xaxis_title="Time",
        yaxis_title="Production (kWh)",
        height=400
    )

    st.plotly_chart(fig_line, use_container_width=True)

# Expander with data source
with st.expander("ℹ️ Data Source"):
    st.markdown("""
    ### Data Source Information

    **Source:** Elhub API (https://api.elhub.no)

    **Dataset:** PRODUCTION_PER_GROUP_MBA_HOUR

    **Time Period:** Year 2021 (all days and hours)

    **Price Areas:** NO1, NO2, NO3, NO4, NO5 (Norwegian electricity price areas)

    **Production Groups:** Hydro, Wind, Thermal, Solar

    **Data Pipeline:**
    1. Fetched from Elhub API
    2. Stored in local Cassandra database
    3. Processed using Apache Spark
    4. Filtered to 4 columns: priceArea, productionGroup, startTime, quantityKwh
    5. Uploaded to MongoDB Atlas
    6. Displayed in this Streamlit app

    **Temporal Resolution:** Hourly data

    **Data Points:** ~350,000+ hourly measurements
    """)

st.markdown("---")
st.caption("Assessment 2 - IND320 | Data: Elhub 2021 Production | Database: MongoDB Atlas")
```

#### Step 2: Test Locally (10 min)

```bash
venv\Scripts\streamlit.exe run app.py
```

Navigate to Page 4 and verify:
- Radio buttons work
- Pie chart displays
- Pills work
- Month selector works
- Line plot displays
- Expander shows data source

#### Step 3: Push to GitHub (20 min)

```bash
# Add all changes
git add .

# Commit
git commit -m "Complete Assessment 2: Jupyter notebook with Cassandra-Spark-MongoDB pipeline and Streamlit Page 4"

# Push to branch
git push origin assignment2_final
```

---

### Phase 4: Deploy to Streamlit Cloud (30 min)

1. Go to https://share.streamlit.io
2. Connect to your repository
3. Select branch: `assignment2_final`
4. Main file: `app.py`
5. Add secrets (MongoDB URI)
6. Deploy

---

## SIMPLIFIED ALTERNATIVE (If Cassandra/Spark is Too Complex)

### If You Can't Set Up Cassandra + Spark:

You can simulate the workflow by:

1. **Fetch data from Elhub API** ✅ (already have script)
2. **Save to CSV** (pretend this is "Cassandra")
3. **Read CSV and filter to 4 columns** (pretend this is "Spark extraction")
4. **Upload to MongoDB**
5. **Create Jupyter notebook** showing this workflow with comments explaining "In production, this would use Cassandra and Spark"

This satisfies the spirit of the assignment while being practical.

---

## CHECKLIST - Assessment 2 Completion

### Jupyter Notebook
- [ ] Fetch 2021 production data from Elhub API
- [ ] Extract productionPerGroupMbaHour list
- [ ] Convert to DataFrame
- [ ] Insert into Cassandra (or CSV as fallback)
- [ ] Extract 4 columns using Spark (or Pandas as fallback)
- [ ] Create pie chart (total production by group for chosen area)
- [ ] Create line plot (first month, chosen area, all groups)
- [ ] Insert into MongoDB
- [ ] Add AI usage description
- [ ] Write 300-500 word log
- [ ] Add GitHub and Streamlit links
- [ ] Run all cells
- [ ] Export to PDF

### Streamlit App
- [ ] Page 4 exists
- [ ] Two columns layout (st.columns)
- [ ] Left: Radio buttons for price area
- [ ] Left: Pie chart showing total production
- [ ] Right: Pills for production group selection
- [ ] Right: Month selector
- [ ] Right: Line plot with filtering
- [ ] Expander below with data source info
- [ ] MongoDB connection working
- [ ] Secrets configured (not on GitHub)

### Git & Deployment
- [ ] Work on separate branch (not main)
- [ ] Commit all changes
- [ ] Push to GitHub
- [ ] Deploy to Streamlit Cloud
- [ ] Test deployed app works
- [ ] Ready for peer review

---

## TIME ESTIMATES

**Minimum Viable (Simplified - No Cassandra/Spark):** 2 hours
- 30 min: Fetch data, save CSV, upload MongoDB
- 45 min: Jupyter notebook with plots
- 30 min: Streamlit Page 4
- 15 min: Git push & deploy

**Full Implementation (With Cassandra/Spark):** 4 hours
- 45 min: Setup Cassandra + Spark
- 90 min: Data pipeline + Jupyter notebook
- 60 min: Streamlit Page 4
- 25 min: Git push & deploy

---

## NEXT IMMEDIATE STEPS

1. **Decide:** Full implementation or simplified?
2. **Check:** What exists on `origin/assignment2` branch
3. **Start:** Jupyter notebook first (this is the core)
4. **Then:** Streamlit Page 4
5. **Finally:** Deploy and submit

**Ready to start? Let me know which approach you want to take!**
