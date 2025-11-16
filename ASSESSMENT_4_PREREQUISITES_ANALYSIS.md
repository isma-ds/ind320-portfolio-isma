# Assessment 4 - Prerequisites Analysis & Critical Questions

## Analysis Date: 2025-11-16

---

## Executive Summary

After thorough analysis of the codebase across all git branches (assignment2, assignment3_update, main), here's what exists and what's needed for Assessment 4.

**CRITICAL FINDING:** The current implementation uses **SYNTHETIC DATA ONLY** - there is NO real Elhub API integration. This is a major blocker for Assessment 4 requirements.

---

## What Currently EXISTS

### 1. Git Repository Structure
- **Repository:** `ind320-portfolio-isma` (GitHub: isma-ds/ind320-portfolio-isma)
- **Branches:**
  - `main` - Contains Assignment 2 code
  - `origin/assignment2` - Assignment 2 final version
  - `origin/assignment2_update` - Assignment 2 updates
  - `origin/assignment3_update` - Assignment 3 (most recent work)
  - `origin/feature/mongodb_streamlit_update` - Feature branch
  - `origin/part2-elhub-mongo-cassandra` - Early work

### 2. Existing Jupyter Notebooks
- **Assignment 1:** `notebooks/IND320_part1.ipynb`
- **Assignment 2:** `notebooks/IND320_Part2.ipynb`
- **Assignment 3:** `notebooks/IND320_Assignment3.ipynb` (in assignment3_update branch)

### 3. Existing Streamlit App (Assignment 3)
**Location:** `assignment3_update` branch

**Pages:**
- `app.py` - Main entry point
- `pages/02_PriceArea.py` - Price area selector
- `pages/03_Analysis_A.py` - Weather analysis (STL + Spectrogram)
- `pages/04_DataTable.py` - Data table view
- `pages/05_PlotPage.py` - Plotting page
- `pages/06_Analysis_B.py` - Production anomalies (SPC + LOF)
- `pages/07_Mongo_Status.py` - MongoDB connection status

**Libraries:**
- `lib/open_meteo.py` - Open-Meteo API integration (ERA5 data)
- `notebooks/utils_analysis.py` - Analysis utilities

### 4. Database Configuration

#### MongoDB (EXISTS - Cloud Hosted)
- **Provider:** MongoDB Atlas
- **URI:** `mongodb+srv://ismasohail_user:IsmaMinhas@cluster0.e3wct64.mongodb.net/ind320?retryWrites=true&w=majority&appName=Cluster0`
- **Database:** `ind320`
- **Collection:** `elhub_prod_2021`
- **Data:** Synthetic 2021 production data (5,376 records)
  - 4 price areas: NO1, NO2, NO3, NO4
  - 4 production groups: HYDRO, THERMAL, SOLAR, WIND
  - Monthly data (Jan-Dec 2021)
  - Randomly generated values
- **Status:** Working and accessible
- **Streamlit Integration:** Uses `st.secrets.get("MONGO_URI")` for deployment

**WARNING:** The credentials are HARDCODED in the Assignment 2 notebook - this is a security risk!

#### Cassandra (DOES NOT EXIST - Simulated Only)
- **Status:** NOT RUNNING
- **Implementation:** Simulated using Spark in-memory DataFrames
- **Reason:** Assignment 2 notes state "due to authentication limitations in the Astra environment"
- **Conclusion:** Cassandra was NEVER actually set up

### 5. External Data Sources

#### Open-Meteo API (EXISTS - Working)
- **Purpose:** Weather data (ERA5 reanalysis)
- **Integration:** `lib/open_meteo.py`
- **Status:** Free API, no credentials needed
- **Usage:** Temperature, precipitation, wind data for Assignment 3
- **Working:** YES

#### Elhub API (DOES NOT EXIST)
- **Status:** NOT INTEGRATED
- **Current Data:** 100% synthetic/simulated
- **API Credentials:** NONE FOUND
- **Conclusion:** No real Elhub data has been fetched

### 6. Existing Data Files

**In `data/` folder:**
- `production_per_group_mba_hour.csv` - Synthetic production data
- `open-meteo-subset.csv` - Weather data cache

### 7. Python Environment

**Confirmed Packages (from requirements.txt):**
- streamlit >= 1.39
- pandas >= 2.2
- numpy >= 1.26
- plotly >= 5.23
- scikit-learn >= 1.5
- statsmodels >= 0.14
- scipy >= 1.11
- requests >= 2.32
- matplotlib >= 3.8
- pymongo

**MISSING Packages for Assessment 4:**
- cassandra-driver (for Cassandra)
- pyspark (for Spark - mentioned in A2 but not in requirements)
- folium (if choosing Folium for maps instead of Plotly)
- Any SARIMAX dependencies (statsmodels should cover this)

---

## What is MISSING (Critical Blockers)

### 1. ELHUB API CREDENTIALS (CRITICAL)
- **Status:** NOT FOUND
- **Impact:** Cannot fetch real production/consumption data for 2021-2024
- **Assessment 4 Requirement:** Fetch data for:
  - `PRODUCTION_PER_GROUP_MBA_HOUR` (2022-2024)
  - `CONSUMPTION_PER_GROUP_MBA_HOUR` (2021-2024)
- **Action Needed:** Ask instructor for Elhub API access

### 2. CASSANDRA DATABASE (CRITICAL)
- **Status:** NEVER SET UP (only simulated)
- **Impact:** Cannot store 2022-2024 data as required
- **Assessment 4 Requirement:** Store data in Cassandra using Spark
- **Action Needed:** Decide if Cassandra is actually required or if MongoDB is sufficient

### 3. SPARK CONFIGURATION (CRITICAL)
- **Status:** Used in Assignment 2 but configuration unclear
- **Impact:** Cannot process large datasets for Cassandra
- **Assessment 4 Requirement:** Use Spark to write to Cassandra
- **Action Needed:** Clarify if Spark is mandatory or optional

### 4. GEOJSON DATA FILES (NEEDED)
- **Status:** NOT DOWNLOADED YET
- **Impact:** Cannot create map visualization
- **Required Files:**
  1. Norwegian Price Areas (NO1-NO5) from https://temakart.nve.no/tema/nettanlegg
  2. (Bonus) Municipality boundaries from http://kartkatalog.geonorge.no
- **Action Needed:** Download GeoJSON files before implementation

### 5. SNOW_DRIFT.PY FILE (NEEDED)
- **Status:** NOT FOUND in repository
- **Impact:** Cannot implement snow drift calculations
- **Assessment 4 Requirement:** "Copy and edit relevant parts of supplied file Snow_drift.py"
- **Action Needed:** Ask instructor for Snow_drift.py file

### 6. REAL 2021-2024 DATA (CRITICAL)
- **Status:** ALL DATA IS SYNTHETIC
- **Impact:** Cannot perform real analysis
- **Current Data Coverage:**
  - 2021 production: Synthetic (in MongoDB)
  - 2021 consumption: DOES NOT EXIST
  - 2022-2024 production: DOES NOT EXIST
  - 2022-2024 consumption: DOES NOT EXIST
- **Action Needed:** Get real data or clarify if synthetic is acceptable

---

## Questions to Ask Your Instructor (URGENT)

### Critical Questions (Must Ask)

1. **Elhub API Access**
   - "How do we access the Elhub API to fetch production and consumption data?"
   - "Do you provide API credentials, or should we use synthetic data?"
   - "Is there a specific endpoint or Python library for Elhub integration?"

2. **Cassandra Requirement**
   - "In Assignment 2, Cassandra was simulated. For Assessment 4, is a real Cassandra instance required?"
   - "Can we use MongoDB only, or is Cassandra mandatory?"
   - "If Cassandra is required, should we use Astra DB, local Cassandra, or continue simulation?"

3. **Snow_drift.py File**
   - "The requirements mention a supplied file 'Snow_drift.py' - where can we find this file?"
   - "Is this file available on the course website or should it have been shared earlier?"

4. **Real vs Synthetic Data**
   - "Is it acceptable to use synthetic/simulated data for Assessment 4?"
   - "If we cannot access real Elhub data, what alternative data source should we use?"

5. **Spark Configuration**
   - "Is Apache Spark mandatory for Assessment 4?"
   - "If yes, what version and configuration do you recommend?"
   - "Can we process data with Pandas instead of Spark if datasets are manageable?"

### Clarification Questions (Important)

6. **2021 Consumption Data**
   - "Should we fetch consumption data for 2021, or only use the 2021 production data from Assignment 2?"
   - "The requirement says 'CONSUMPTION_PER_GROUP_MBA_HOUR for all days and hours of years 2021-2024' - does this include 2021 or start from 2022?"

7. **Data Scope**
   - "The requirement mentions 'all Norwegian price areas' - how many are there? NO1-NO5 or more?"
   - "Should we fetch hourly data for ALL hours of 2022-2024, or is a sample acceptable for demonstration?"

8. **GeoJSON Coordinate System**
   - "The instructions mention 'EUREF 89 Geografisk (ETRS 89) 2d format' - do the GeoJSON files need conversion, or are they already in the correct format?"

9. **Deployment Credentials**
   - "For Streamlit Cloud deployment, how should we handle sensitive credentials (MongoDB, Elhub API)?"
   - "Is it acceptable to use Streamlit secrets, or do you require environment variables?"

10. **Deadline and Revisions**
    - "What is the final deadline for Assessment 4?"
    - "The requirements mention 'subject to revisions before deadline, especially during first week' - have there been any updates since November 11?"

---

## Current State Assessment

### What Works (Ready to Use)
1. ✅ GitHub repository with proper branch structure
2. ✅ MongoDB Atlas connection with credentials
3. ✅ Open-Meteo API integration for weather data
4. ✅ Streamlit app framework from Assignment 3
5. ✅ Python environment with most required packages
6. ✅ Existing Jupyter Notebook structure
7. ✅ Experience with data visualization (Plotly, Matplotlib)
8. ✅ 2021 synthetic production data in MongoDB

### What Doesn't Work (Blockers)
1. ❌ NO Elhub API access or credentials
2. ❌ NO real production/consumption data (all synthetic)
3. ❌ NO Cassandra database (only simulated)
4. ❌ NO 2021 consumption data
5. ❌ NO 2022-2024 data of any kind
6. ❌ NO Snow_drift.py file
7. ❌ NO GeoJSON data files
8. ❌ Unclear Spark configuration

### What Might Work (Needs Testing)
1. ⚠️ MongoDB can store 2021-2024 data (if we get it)
2. ⚠️ Streamlit deployment to Cloud (credentials in secrets)
3. ⚠️ SARIMAX forecasting (statsmodels installed)
4. ⚠️ Map visualization with Plotly (library installed)

---

## Recommended Approach (After Getting Answers)

### Option A: If Real Elhub API is Available
1. Get API credentials from instructor
2. Implement Elhub data fetching in Jupyter Notebook
3. Store data in MongoDB (skip Cassandra if not required)
4. Download GeoJSON files
5. Get Snow_drift.py file
6. Implement all Assessment 4 features

### Option B: If Using Synthetic Data (Most Likely)
1. Generate synthetic data matching Elhub schema for:
   - 2022-2024 production data
   - 2021-2024 consumption data
2. Store in MongoDB (existing infrastructure)
3. Download GeoJSON files
4. Get or recreate Snow_drift.py functionality
5. Implement all Assessment 4 features with synthetic data
6. Document clearly that synthetic data was used

### Option C: Alternative Data Source
1. Find publicly available Norwegian energy data
2. Adapt to Elhub schema
3. Proceed with Assessment 4 requirements

---

## What I Can Do NOW (Without Instructor)

### Immediate Actions (No Blockers)
1. ✅ Download GeoJSON data for Norwegian price areas
2. ✅ Set up Assessment 4 git branch
3. ✅ Create Jupyter Notebook template for Assessment 4
4. ✅ Research SARIMAX implementation in Python
5. ✅ Plan Streamlit app structure (on paper/diagram)
6. ✅ Study Plotly/Folium map libraries
7. ✅ Review Assignment 2 & 3 code thoroughly
8. ✅ Create implementation checklist

### Actions Requiring Minor Research (Can Proceed)
1. Create synthetic 2022-2024 production data matching current schema
2. Create synthetic 2021-2024 consumption data
3. Research snow drift calculation methods (to recreate if Snow_drift.py unavailable)
4. Test MongoDB capacity for larger datasets
5. Prototype map visualization with Plotly

### Actions Blocked (Need Instructor Input)
1. ❌ Fetch real Elhub data
2. ❌ Set up Cassandra (if required)
3. ❌ Configure Spark (if mandatory)
4. ❌ Obtain Snow_drift.py file
5. ❌ Finalize data strategy (real vs synthetic)

---

## My Recommendations

### Priority 1: Contact Instructor IMMEDIATELY
**Send email with these questions:**
1. How to access Elhub API?
2. Is Cassandra required or can we use MongoDB only?
3. Where is Snow_drift.py file?
4. Is synthetic data acceptable for Assessment 4?

### Priority 2: Start Non-Blocked Work
While waiting for answers, I can:
1. Download GeoJSON files for maps
2. Create Assessment 4 branch and notebook structure
3. Generate synthetic 2022-2024 data in same format as Assignment 2
4. Research and plan SARIMAX implementation
5. Design Streamlit app navigation structure

### Priority 3: Prepare Both Paths
Create two implementation plans:
- **Plan A:** Real Elhub data (if we get API access)
- **Plan B:** Synthetic data (continuation of Assignment 2 approach)

This way, we can start immediately once we get answers.

---

## Security Issues Found

### CRITICAL: Hardcoded Credentials
**Location:** `notebooks/IND320_Part2.ipynb`

```python
mongo_uri = "mongodb+srv://ismasohail_user:IsmaMinhas@cluster0.e3wct64.mongodb.net/ind320?retryWrites=true&w=majority&appName=Cluster0"
```

**Risk:** Credentials are committed to GitHub (public repository)

**Recommendation:**
1. Change MongoDB password immediately
2. Use environment variables or Streamlit secrets
3. Remove credentials from notebook
4. Add credentials to .gitignore

**Fix for Assessment 4:**
```python
import os
from streamlit import secrets

# In Jupyter Notebook
mongo_uri = os.getenv("MONGO_URI")

# In Streamlit App
mongo_uri = secrets.get("MONGO_URI")
```

---

## Files That Need to Be Created for Assessment 4

### 1. Jupyter Notebook
- `notebooks/IND320_Assignment4.ipynb`
  - Data fetching/generation for 2021-2024
  - MongoDB/Cassandra storage
  - 300-500 word log
  - AI usage description
  - Links to GitHub and Streamlit app

### 2. Streamlit App Components
- Enhanced app.py with new navigation
- New pages:
  - `pages/XX_Map_Selector.py` - Interactive map with GeoJSON
  - `pages/XX_Energy_Choropleth.py` - Production/consumption visualization
  - `pages/XX_Snow_Drift.py` - Snow drift calculation and wind rose
  - `pages/XX_Correlation.py` - Meteorology-energy correlation
  - `pages/XX_Forecasting.py` - SARIMAX forecasting

### 3. Data Files
- GeoJSON for Norwegian price areas (NO1-NO5)
- (Optional) GeoJSON for municipalities
- 2022-2024 production data (CSV or MongoDB)
- 2021-2024 consumption data (CSV or MongoDB)

### 4. Utility Scripts
- Snow drift calculation functions
- SARIMAX wrapper functions
- Map visualization utilities
- Data fetching/generation scripts

### 5. Documentation
- Updated README
- Updated requirements.txt
- .gitignore updates (for credentials)
- Deployment instructions

---

## Estimated Timeline (After Getting Answers)

### Scenario: Synthetic Data (Most Realistic)
- **Week 1:** Data generation, MongoDB storage, GeoJSON download
- **Week 2:** Map implementation, energy choropleth
- **Week 3:** Snow drift, correlation analysis
- **Week 4:** SARIMAX forecasting
- **Week 5:** Bonus features, documentation
- **Week 6:** Testing, deployment, peer review
- **Week 7:** Final submission

### Scenario: Real Elhub API
- **Week 1-2:** API integration, data fetching, database storage
- **Week 3:** Map implementation, energy choropleth
- **Week 4:** Snow drift, correlation analysis
- **Week 5:** SARIMAX forecasting
- **Week 6:** Bonus features, documentation
- **Week 7:** Testing, deployment, peer review
- **Week 8:** Final submission

---

## Summary: What You Need to Provide

### From You (User)
1. Contact your instructor with the 10 questions above
2. Share their responses with me
3. Confirm deadline for Assessment 4
4. Approve implementation approach (synthetic vs real data)

### From Instructor (Critical)
1. Elhub API access OR confirmation to use synthetic data
2. Snow_drift.py file OR permission to recreate
3. Cassandra requirement clarification
4. Any updates to requirements since November 11

### Once I Have Answers
I can create a detailed, step-by-step implementation plan and begin coding Assessment 4.

---

## Next Steps

**WAIT FOR YOUR APPROVAL** before proceeding with any of these:

1. Download GeoJSON files for Norwegian price areas
2. Create Assessment 4 git branch
3. Generate synthetic 2022-2024 production data
4. Generate synthetic 2021-2024 consumption data
5. Set up Assessment 4 Jupyter Notebook
6. Begin map implementation planning

**I will NOT write any code until:**
1. You've contacted your instructor with the critical questions
2. You've shared their responses with me
3. You've approved the implementation approach
4. You've said "you can go ahead and start working on this"

---

## Current Status: AWAITING YOUR DECISION

I've completed my analysis. I'm ready to work but need your input on how to proceed.

**Tell me:**
1. Should I draft an email for you to send to your instructor?
2. Do you want me to proceed with synthetic data approach while waiting?
3. Should I download the GeoJSON files now (non-blocking task)?
4. Any other preferences or concerns?
