# Deployment Guide - IND320 Assessment 4

## Complete Setup Instructions for Real Data Integration

This guide walks through deploying the Assessment 4 application with **real Elhub API data** and **local Cassandra database**.

---

## Overview

The application now supports:
- Real Elhub API data (publicly accessible, no authentication required)
- Local 3-node Cassandra cluster (Docker-based)
- MongoDB Atlas cloud database (existing)
- Tabler (2003) snow drift physics calculations
- All 5 Streamlit analysis pages

---

## Prerequisites

### Required Software

1. **Docker Desktop**
   - Download: https://www.docker.com/products/docker-desktop
   - Minimum 4GB RAM allocated to Docker
   - Windows: WSL2 backend recommended

2. **Python 3.12+**
   - Download: https://www.python.org/downloads/
   - Add to PATH during installation

3. **Git**
   - Download: https://git-scm.com/downloads

### Required Packages

```bash
pip install -r requirements.txt
```

Key packages:
- streamlit>=1.39
- pandas>=2.2
- pymongo>=4.5
- cassandra-driver>=3.29
- plotly>=5.23
- statsmodels>=0.14

---

## Step-by-Step Deployment

### 1. Clone Repository

```bash
git clone https://github.com/isma-ds/ind320-portfolio-isma.git
cd ind320-portfolio-isma
git checkout assessment4
```

### 2. Fetch Real Elhub Data

The Elhub API is publicly accessible with no authentication required.

```bash
python scripts/fetch_elhub_data.py
```

This will download:
- Consumption 2021: `data/elhub_consumption_2021.csv`
- Consumption 2022-2024: `data/elhub_consumption_2022_2024.csv`
- Production 2022-2024: `data/elhub_production_2022_2024.csv`

**API Endpoints Used:**
- https://api.elhub.no/energy-data/v0/price-areas?dataset=CONSUMPTION_PER_GROUP_MBA_HOUR
- https://api.elhub.no/energy-data/v0/price-areas?dataset=PRODUCTION_PER_GROUP_MBA_HOUR

**Expected Output:**
```
[OK] Retrieved XXXXX consumption records for 2021
[OK] Retrieved XXXXX consumption records for 2022-2024
[OK] Retrieved XXXXX production records for 2022-2024
Total records fetched: XXXXX
```

### 3. Start Cassandra Cluster

#### Windows:

```bash
cassandra_manager.bat start
```

#### Mac/Linux:

```bash
docker-compose up -d
```

**Wait 2-3 minutes** for cluster initialization.

Check status:

```bash
# Windows
cassandra_manager.bat status

# Mac/Linux
docker-compose ps
```

All 3 nodes should show "Up" status:
- cassandra1 (seed node)
- cassandra2
- cassandra3

### 4. Initialize Cassandra Schema

```bash
# Windows
cassandra_manager.bat init

# Mac/Linux
docker exec -i cassandra1 cqlsh < cassandra-init/init.cql
```

This creates:
- Keyspace: `ind320` (replication factor 3)
- Tables: `elhub_consumption_2021`, `elhub_consumption_2022_2024`, `elhub_production_2022_2024`

### 5. Upload Data to Cassandra

```bash
# Windows
cassandra_manager.bat upload

# Mac/Linux
python scripts/upload_to_cassandra.py
```

**Upload Progress:**
```
[UPLOAD] Loading data/elhub_consumption_2021.csv...
[OK] Loaded XXXXX records from CSV
[PROGRESS] Uploaded 1000/XXXXX records...
[PROGRESS] Uploaded 2000/XXXXX records...
...
[OK] Successfully uploaded XXXXX records to elhub_consumption_2021
```

### 6. Verify Cassandra Data

Access CQL shell:

```bash
# Windows
cassandra_manager.bat shell

# Mac/Linux
docker exec -it cassandra1 cqlsh
```

Run verification queries:

```sql
USE ind320;

-- Check tables exist
DESCRIBE TABLES;

-- Verify data (replace COUNT with LIMIT for speed)
SELECT * FROM elhub_consumption_2021 LIMIT 10;
SELECT * FROM elhub_consumption_2022_2024 LIMIT 10;
SELECT * FROM elhub_production_2022_2024 LIMIT 10;

-- Check specific price area and group
SELECT * FROM elhub_consumption_2021
WHERE priceArea = 'NO1'
AND consumptionGroup = 'residential'
LIMIT 5;

-- Exit
exit;
```

### 7. Configure Streamlit Secrets (Optional for MongoDB)

If using MongoDB Atlas:

```bash
# Create secrets file
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml`:

```toml
MONGO_URI = "mongodb+srv://username:password@cluster.mongodb.net/ind320?retryWrites=true&w=majority"
```

### 8. Run Streamlit Application

```bash
streamlit run app.py
```

The app will open at: http://localhost:8501

### 9. Test All Features

#### a. Interactive Map
1. Navigate to "Interactive Map" in sidebar
2. Click on Norway to select coordinates
3. Or enter manually: Oslo (59.9, 10.7)
4. Verify coordinates stored in session state

#### b. Energy Choropleth
1. Go to "Energy Choropleth"
2. Select "Consumption" and "Residential"
3. Choose date range in 2021
4. Verify choropleth map displays correctly
5. Check that data comes from Cassandra

#### c. Snow Drift
1. Navigate to "Snow Drift"
2. Ensure coordinates are set (from map)
3. Select year range 2021-2022
4. Verify Tabler (2003) metrics display:
   - Mean Annual Snow Transport (Qt) in tonnes/m
   - Potential Transport (Qupot)
   - Process Control (Wind/Snowfall controlled)
5. Check wind rose shows directional transport

#### d. Correlation Analysis
1. Open "Correlation Analysis"
2. Select weather variable (e.g., Temperature)
3. Select energy metric (e.g., Hydro production)
4. Adjust window size (30 days)
5. Try different lag values (-10 to +10)
6. Verify correlation plot displays

#### e. SARIMAX Forecasting
1. Go to "SARIMAX Forecasting"
2. Select energy metric
3. Choose training period (2021-01-01 to 2021-06-30)
4. Set simple parameters: p=1, d=1, q=1, P=1, D=1, Q=1, s=24
5. Select exogenous variables (temperature, precipitation)
6. Click "Train Model"
7. Verify forecast plot with confidence intervals

---

## Architecture

### Data Flow

```
Elhub API → Python Script → CSV Files → Cassandra/MongoDB → Streamlit App
                ↓                           ↑
            fetch_elhub_data.py      cassandra_client.py
```

### Cassandra Cluster

- **Nodes**: 3 (cassandra1, cassandra2, cassandra3)
- **Replication**: Factor 3 (all data on all nodes)
- **Consistency**: QUORUM (2/3 nodes must respond)
- **Ports**:
  - Node 1: 9042 (CQL)
  - Node 2: 9043
  - Node 3: 9044

### Database Comparison

| Feature | MongoDB | Cassandra |
|---------|---------|-----------|
| Deployment | Cloud (Atlas) | Local (Docker) |
| Data Model | Document (JSON) | Wide-column |
| Query | MongoDB API | CQL (SQL-like) |
| Consistency | Strong | Tunable |
| Scaling | Vertical + Horizontal | Linear horizontal |
| Use Case | Complex queries | Time-series, high writes |

---

## File Structure

```
ind320-portfolio-isma/
├── app.py                          # Main Streamlit homepage
├── pages/
│   ├── 08_Interactive_Map.py       # GeoJSON map
│   ├── 09_Energy_Choropleth.py     # Energy visualization
│   ├── 10_Snow_Drift.py            # Tabler (2003) snow drift
│   ├── 11_Correlation_Analysis.py  # Weather-energy correlation
│   └── 12_SARIMAX_Forecasting.py   # Time series forecasting
├── scripts/
│   ├── fetch_elhub_data.py         # Download real Elhub data
│   ├── upload_to_cassandra.py      # Upload to Cassandra
│   └── upload_to_mongodb.py        # Upload to MongoDB
├── cassandra_client.py             # Cassandra data access layer
├── snow_drift.py                   # Original Tabler (2003) formulas
├── docker-compose.yml              # 3-node Cassandra cluster
├── cassandra-init/
│   └── init.cql                    # Database schema
├── cassandra_manager.bat           # Windows cluster manager
├── data/                           # Real Elhub CSV data
├── geojson_data/
│   └── elspot_areas.geojson        # Norwegian price areas
├── requirements.txt                # Python dependencies
├── CASSANDRA_SETUP.md              # Cassandra guide
├── DEPLOYMENT_GUIDE.md             # This file
└── notebooks/
    └── IND320_Assignment4.ipynb    # Jupyter notebook
```

---

## Troubleshooting

### Elhub API Issues

**Problem:** "No data fetched from API"

Solutions:
1. Check internet connection
2. Verify API endpoints are accessible:
   ```bash
   curl "https://api.elhub.no/energy-data/v0/price-areas?dataset=CONSUMPTION_PER_GROUP_MBA_HOUR"
   ```
3. Check date ranges (API may have limited historical data)
4. Try different year ranges

### Cassandra Issues

**Problem:** "Could not connect to Cassandra"

Solutions:
1. Verify Docker is running: `docker ps`
2. Check cluster status: `cassandra_manager.bat status`
3. Wait longer (cluster needs 2-3 minutes to initialize)
4. Check logs: `cassandra_manager.bat logs cassandra1`
5. Restart cluster:
   ```bash
   cassandra_manager.bat stop
   cassandra_manager.bat start
   ```

**Problem:** "Out of memory"

Solutions:
1. Increase Docker memory allocation (Settings → Resources)
2. Reduce heap size in `docker-compose.yml`:
   ```yaml
   MAX_HEAP_SIZE=512M
   HEAP_NEWSIZE=100M
   ```
3. Run with 1-2 nodes instead of 3 (comment out in docker-compose.yml)

**Problem:** "ALLOW FILTERING warning"

- This is expected for queries without partition key
- Performance may be slow on large datasets
- Consider adding WHERE clauses with priceArea and group

### Streamlit Issues

**Problem:** "Module not found: cassandra_client"

Solution:
```bash
# Ensure cassandra_client.py is in root directory
ls cassandra_client.py

# Run from project root
cd ind320-portfolio-isma
streamlit run app.py
```

**Problem:** "Cassandra: Not configured" in sidebar

- Normal if Cassandra is not running
- App will use MongoDB instead
- Not an error, just informational

### Snow Drift Issues

**Problem:** "No meteorological data available"

Solutions:
1. Check coordinates are valid (Norway: lat 58-71, lon 4-31)
2. Verify Open-Meteo API is accessible
3. Try different date ranges (ERA5 has historical data from 1940+)
4. Check internet connection

---

## Performance Optimization

### Cassandra Query Optimization

1. **Always use partition key** in WHERE clause:
   ```sql
   -- Good (uses partition key)
   SELECT * FROM elhub_consumption_2021
   WHERE priceArea = 'NO1' AND consumptionGroup = 'residential'
   AND startTime >= '2021-01-01';

   -- Bad (requires ALLOW FILTERING)
   SELECT * FROM elhub_consumption_2021
   WHERE startTime >= '2021-01-01';
   ```

2. **Limit result sets**:
   ```sql
   SELECT * FROM elhub_consumption_2021 LIMIT 1000;
   ```

3. **Use time ranges efficiently**:
   ```sql
   SELECT * FROM elhub_consumption_2021
   WHERE priceArea = 'NO1' AND consumptionGroup = 'residential'
   AND startTime >= '2021-01-01' AND startTime < '2021-02-01';
   ```

### Streamlit Caching

All data fetching functions use `@st.cache_data`:

```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_consumption_data(collection_name, start_date, end_date):
    # ...
```

Clear cache if data changes:
- Streamlit menu → "Clear cache"
- Or restart app

---

## Deployment to Streamlit Cloud

### Prerequisites

1. GitHub repository with assessment4 branch
2. Streamlit Cloud account (free)
3. MongoDB Atlas connection string (for cloud deployment)

### Steps

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Assessment 4 complete with real Elhub data and Cassandra"
   git push origin assessment4
   ```

2. **Create Streamlit Cloud App:**
   - Go to https://share.streamlit.io/
   - Click "New app"
   - Select repository: `isma-ds/ind320-portfolio-isma`
   - Branch: `assessment4`
   - Main file: `app.py`

3. **Configure Secrets:**
   - In Streamlit Cloud dashboard
   - Advanced settings → Secrets
   - Add:
     ```toml
     MONGO_URI = "mongodb+srv://..."
     ```

4. **Deploy:**
   - Click "Deploy"
   - Wait for build to complete
   - Test deployed app

**Note:** Cassandra cluster is local only. Streamlit Cloud deployment will use MongoDB exclusively.

---

## Next Steps

1. Test all 5 pages with real data
2. Verify snow drift calculations match Tabler (2003) formulas
3. Export Jupyter Notebook to PDF for submission
4. Create pull request for peer review
5. Deploy to Streamlit Cloud (optional)
6. Merge to main branch after approval

---

## Support & Resources

### Documentation

- [Cassandra Setup Guide](CASSANDRA_SETUP.md)
- [Assessment Overview](ASSESSMENT_4_OVERVIEW.md)
- [Implementation Complete](ASSESSMENT_4_COMPLETE.md)

### External Links

- Elhub API: https://api.elhub.no/downloads
- Cassandra Docs: https://cassandra.apache.org/doc/latest/
- Streamlit Docs: https://docs.streamlit.io/
- Open-Meteo API: https://open-meteo.com/

### Contact

- Student: Isma Sohail
- Course: IND320 - NMBU
- GitHub: https://github.com/isma-ds/ind320-portfolio-isma

---

**Assessment 4 - IND320**
**Last Updated**: 2025-11-17
**Status**: Production Ready
