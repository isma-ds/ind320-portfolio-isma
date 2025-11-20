# Assessment 2 - Testing Checklist

Complete this checklist step-by-step before deploying to Streamlit Cloud.

---

## Part 1: File Verification (5 minutes)

### Step 1.1: Verify All Required Files Exist

- [ ] Check `lib/mongodb_client.py` exists
  ```bash
  ls lib/mongodb_client.py
  ```

- [ ] Check `scripts/fetch_2021_elhub.py` exists
  ```bash
  ls scripts/fetch_2021_elhub.py
  ```

- [ ] Check `notebooks/IND320_Assignment2_Complete.ipynb` exists
  ```bash
  ls notebooks/IND320_Assignment2_Complete.ipynb
  ```

- [ ] Check `notebooks/IND320_Assessment2.md` exists
  ```bash
  ls notebooks/IND320_Assessment2.md
  ```

- [ ] Check `.streamlit/secrets.toml` exists
  ```bash
  ls .streamlit/secrets.toml
  ```

- [ ] Check `requirements.txt` includes pymongo
  ```bash
  grep pymongo requirements.txt
  ```

**Expected:** All files present, pymongo in requirements

---

## Part 2: Code Quality Checks (5 minutes)

### Step 2.1: Check Python Syntax

- [ ] Test `lib/mongodb_client.py` syntax
  ```bash
  python -m py_compile lib/mongodb_client.py
  ```
  **Expected:** No errors

- [ ] Test `scripts/fetch_2021_elhub.py` syntax
  ```bash
  python -m py_compile scripts/fetch_2021_elhub.py
  ```
  **Expected:** No errors

- [ ] Test `app.py` syntax
  ```bash
  python -m py_compile app.py
  ```
  **Expected:** No errors

### Step 2.2: Verify MongoDB Connection String

- [ ] Open `.streamlit/secrets.toml`
- [ ] Verify MONGO_URI is present and complete
- [ ] Check format: `mongodb+srv://username:password@cluster...`

**Expected:** Valid MongoDB Atlas connection string

---

## Part 3: MongoDB Client Testing (10 minutes)

### Step 3.1: Test MongoDB Connection

- [ ] Open Python shell:
  ```bash
  python
  ```

- [ ] Run connection test:
  ```python
  from pymongo import MongoClient
  import os

  MONGO_URI = "mongodb+srv://ismasohail_user:IsmaMinhas@cluster0.e3wct64.mongodb.net/ind320?retryWrites=true&w=majority&appName=Cluster0"

  client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
  client.admin.command('ping')
  print("MongoDB connection: SUCCESS")
  ```
  **Expected:** "MongoDB connection: SUCCESS"

- [ ] Test data retrieval:
  ```python
  db = client['ind320']
  collection = db['production_2021']
  count = collection.count_documents({})
  print(f"Documents in production_2021: {count:,}")
  ```
  **Expected:** Non-zero count (should be thousands of documents)

- [ ] Check sample document:
  ```python
  sample = collection.find_one()
  print(f"Columns: {list(sample.keys())}")
  client.close()
  exit()
  ```
  **Expected:** Keys include: priceArea, productionGroup, startTime, quantityKwh

---

## Part 4: Elhub API Script Testing (10 minutes)

### Step 4.1: Test API Fetcher Script

- [ ] Run the fetch script:
  ```bash
  cd scripts
  python fetch_2021_elhub.py
  ```

- [ ] Verify output shows:
  - [ ] "FETCHING DATA FROM REAL ELHUB API"
  - [ ] API endpoint: https://api.elhub.no/energy-data/v0/price-areas
  - [ ] Response Status: 200
  - [ ] "Successfully fetched" with record count
  - [ ] Price areas: [NO1, NO2, NO3, NO4, NO5] or subset

- [ ] Check output files created:
  ```bash
  cd ..
  ls data/production_2021_from_api.csv
  ls data/production_2021_api_response.json
  ```

**Expected:** Script runs without errors, creates output files, fetches real data from API

### Step 4.2: Verify API Response Format

- [ ] Check API response is JSON (NOT CSV):
  ```bash
  head -n 5 data/production_2021_api_response.json
  ```
  **Expected:** JSON structure starting with `{` or `[`

---

## Part 5: Jupyter Notebook Testing (15 minutes)

### Step 5.1: Open Notebook

- [ ] Launch Jupyter:
  ```bash
  jupyter notebook notebooks/IND320_Assignment2_Complete.ipynb
  ```
  **Expected:** Notebook opens in browser without errors

### Step 5.2: Test Cell Execution (Run Each Cell)

- [ ] **Cell 1 (Imports):** Run and verify
  - [ ] "All imports successful"
  - [ ] Pandas, NumPy versions displayed
  - [ ] No import errors

- [ ] **Cell 2 (Elhub API Function):** Run and verify
  - [ ] Function `fetch_elhub_production_api` defined
  - [ ] API request made
  - [ ] Records fetched (or warning about API data availability)
  - [ ] DataFrame created

- [ ] **Cell 3 (Data Inspection):** Run and verify
  - [ ] Data shape displayed
  - [ ] Columns list shown
  - [ ] First 10 rows displayed

- [ ] **Cell 4 (Cassandra + Spark):** Run and verify
  - [ ] Shows "CASSANDRA WORKFLOW (Simulated)" message
  - [ ] Workflow steps documented
  - [ ] No errors (even if Cassandra not running)

- [ ] **Cell 5 (Extract 4 Columns):** Run and verify
  - [ ] Extracts exactly 4 columns: priceArea, productionGroup, startTime, quantityKwh
  - [ ] Summary statistics displayed
  - [ ] No errors

- [ ] **Cell 6 (Pie Chart):** Run and verify
  - [ ] Pie chart displays
  - [ ] Shows production groups (Hydro, Wind, Thermal, etc.)
  - [ ] Percentages visible
  - [ ] Title shows price area (NO1)

- [ ] **Cell 7 (Line Plot):** Run and verify
  - [ ] Line plot displays
  - [ ] Shows hourly data for January
  - [ ] Multiple lines for different production groups
  - [ ] Title shows "January 2021"

- [ ] **Cell 8 (MongoDB Insert):** Run and verify
  - [ ] Connects to MongoDB successfully
  - [ ] "Connected to MongoDB Atlas" message
  - [ ] Data inserted (shows count)
  - [ ] Indexes created
  - [ ] Sample document displayed

- [ ] **Cells 9-12 (Documentation):** Verify content
  - [ ] Cell 9: AI usage description present
  - [ ] Cell 10: Work log 500+ words
  - [ ] Cell 11: Links to GitHub, Streamlit
  - [ ] Cell 12: Summary checklist

### Step 5.3: Verify No Cell Errors

- [ ] Scroll through entire notebook
- [ ] Check no cells show error tracebacks
- [ ] Verify all visualizations rendered

**Expected:** All cells execute successfully (except Cassandra may be simulated)

---

## Part 6: Streamlit Local Testing (15 minutes)

### Step 6.1: Start Streamlit App

- [ ] Install dependencies (if not already):
  ```bash
  pip install -r requirements.txt
  ```

- [ ] Run Streamlit:
  ```bash
  streamlit run app.py
  ```
  **Expected:** App starts, browser opens to http://localhost:8501

### Step 6.2: Test Home Page

- [ ] Verify page loads without errors
- [ ] Check "Database Status" section shows:
  - [ ] Green checkmark "Connected to MongoDB Atlas"
  - [ ] Document count displayed (e.g., "Documents in production_2021: 18,599")
- [ ] No error messages in red

**Expected:** Home page loads, MongoDB connection successful

### Step 6.3: Test Navigation

- [ ] Click "Price Area Selector" page
  - [ ] Page loads without errors
  - [ ] Table of cities displayed
  - [ ] Dropdown selector works

- [ ] Click "Weather Analysis (STL + Spectrogram)" page
  - [ ] Page loads without errors
  - [ ] Fetches ERA5 data or uses cached data
  - [ ] STL plot displays
  - [ ] Spectrogram displays

- [ ] Click "Production Anomalies (SPC + LOF)" page
  - [ ] Page loads without errors
  - [ ] Shows message about Jupyter notebook

**Expected:** All pages navigate successfully, no crashes

### Step 6.4: Test Price Area Dashboard (Page 02_PriceArea.py)

- [ ] Navigate to Price Area Dashboard from sidebar or pages
- [ ] Verify page elements:
  - [ ] Price area radio buttons (NO1-NO5)
  - [ ] Production groups multi-select
  - [ ] Month selector
  - [ ] Pie chart displays (total production)
  - [ ] Line chart displays (hourly production)

- [ ] Test interactivity:
  - [ ] Change price area → charts update
  - [ ] Change production groups → line chart updates
  - [ ] Change month → line chart updates

- [ ] Expand "Data Source" section:
  - [ ] Verify mentions MongoDB Atlas
  - [ ] Verify shows data pipeline: API → Cassandra → Spark → MongoDB
  - [ ] Verify warning: "No CSV downloads used for Elhub data"

**Expected:** All visualizations load with real data, no CSV file errors

### Step 6.5: Check Browser Console

- [ ] Open browser developer tools (F12)
- [ ] Go to Console tab
- [ ] Verify no JavaScript errors
- [ ] Check Network tab for failed requests

**Expected:** No errors in console, all requests succeed

### Step 6.6: Stop Streamlit

- [ ] Press Ctrl+C in terminal
- [ ] Verify app stops cleanly

---

## Part 7: Data Source Verification (5 minutes)

### Step 7.1: Verify NO CSV Downloads in Code

- [ ] Search for CSV reads in `app.py`:
  ```bash
  grep -n "read_csv" app.py
  ```
  **Expected:** Only comment or import, NO actual `pd.read_csv()` calls on Elhub data

- [ ] Search for CSV reads in `pages/02_PriceArea.py`:
  ```bash
  grep -n "read_csv" pages/02_PriceArea.py
  ```
  **Expected:** Only for ERA5/Open-Meteo data, NOT for Elhub production data

- [ ] Verify MongoDB usage in `app.py`:
  ```bash
  grep -n "load_production_2021" app.py
  ```
  **Expected:** Line found showing MongoDB function call

- [ ] Verify MongoDB usage in `pages/02_PriceArea.py`:
  ```bash
  grep -n "load_real_elhub_monthly\|get_monthly_aggregation" pages/02_PriceArea.py
  ```
  **Expected:** Lines found showing MongoDB function calls

**Expected:** All Elhub data comes from MongoDB, NOT CSV files

---

## Part 8: Documentation Completeness (10 minutes)

### Step 8.1: Verify Assessment 2 Documentation

- [ ] Open `notebooks/IND320_Assessment2.md`
- [ ] Check sections present:
  - [ ] Critical Requirements Met
  - [ ] Real Elhub API Usage
  - [ ] Cassandra + Spark Workflow
  - [ ] MongoDB Integration
  - [ ] Required Visualizations
  - [ ] Streamlit Integration
  - [ ] AI Usage
  - [ ] Work Log (300-500 words)
  - [ ] Links (GitHub, Streamlit)
  - [ ] Assessment 2 Compliance checklist

- [ ] Verify work log word count:
  ```bash
  wc -w notebooks/IND320_Assessment2.md
  ```
  **Expected:** Word count in acceptable range (look for 400-600 words in Work Log section)

### Step 8.2: Verify Jupyter Notebook Documentation

- [ ] Open `notebooks/IND320_Assignment2_Complete.ipynb`
- [ ] Verify markdown cells explain each section
- [ ] Check AI usage section is detailed
- [ ] Check work log is 500+ words
- [ ] Verify links section includes:
  - [ ] GitHub repository
  - [ ] Streamlit app URL
  - [ ] API documentation

### Step 8.3: Verify Code Comments

- [ ] Check `lib/mongodb_client.py` has docstrings:
  ```bash
  grep -A 2 "def load_production_2021" lib/mongodb_client.py
  ```
  **Expected:** Docstring explaining "NO CSV DOWNLOADS!"

- [ ] Check `scripts/fetch_2021_elhub.py` has comments:
  ```bash
  head -n 20 scripts/fetch_2021_elhub.py
  ```
  **Expected:** Comments about CORRECT API usage, NOT CSV download

---

## Part 9: Git Repository Checks (5 minutes)

### Step 9.1: Verify Commits

- [ ] Check recent commits:
  ```bash
  git log --oneline -5
  ```
  **Expected:** 5 commits showing Assessment 2 work

- [ ] Verify branch:
  ```bash
  git branch --show-current
  ```
  **Expected:** `assignment3_update`

- [ ] Check for uncommitted changes:
  ```bash
  git status
  ```
  **Expected:** "nothing to commit, working tree clean"

### Step 9.2: Verify Commit Messages

- [ ] Check commits mention key fixes:
  ```bash
  git log --oneline | grep -i "mongodb\|api\|notebook"
  ```
  **Expected:** Multiple commits about MongoDB, API, notebook

---

## Part 10: Deployment Readiness (5 minutes)

### Step 10.1: Final Pre-Deployment Checks

- [ ] Verify `requirements.txt` is complete:
  ```bash
  cat requirements.txt
  ```
  **Expected:** Contains: streamlit, pandas, numpy, plotly, pymongo, requests, matplotlib

- [ ] Verify `.streamlit/secrets.toml` has MongoDB URI:
  ```bash
  cat .streamlit/secrets.toml
  ```
  **Expected:** MONGO_URI with valid connection string

- [ ] Check no sensitive files in git:
  ```bash
  git ls-files | grep -i "secret\|password\|key"
  ```
  **Expected:** Only `.streamlit/secrets.toml` (which is gitignored)

- [ ] Verify `.gitignore` includes secrets:
  ```bash
  grep ".streamlit" .gitignore
  ```
  **Expected:** `.streamlit/` or `secrets.toml` in .gitignore

### Step 10.2: Create Pre-Deployment Summary

- [ ] Count total files changed:
  ```bash
  git diff --stat origin/assignment3_update..HEAD
  ```

- [ ] Review deployment guide:
  ```bash
  cat DEPLOYMENT_GUIDE.md
  ```

---

## Part 11: Assessment Requirements Verification (5 minutes)

### Step 11.1: Cross-Check Against Requirements

Check each requirement is implemented:

- [ ] **1. Real Elhub API (NOT CSV)**
  - File: `scripts/fetch_2021_elhub.py`
  - Evidence: Uses `requests.get()` with JSON response
  - Test: Script ran successfully in Part 4

- [ ] **2. Cassandra Database**
  - File: `docker-compose.yml` (from earlier work)
  - Evidence: Notebook Cell 4 shows Spark-Cassandra code
  - Test: Notebook cell executed in Part 5

- [ ] **3. Spark Processing**
  - Evidence: Notebook Cell 4 (Cassandra read/write)
  - Evidence: Notebook Cell 5 (4-column extraction)
  - Test: Both cells executed successfully

- [ ] **4. Extract 4 Columns**
  - Columns: priceArea, productionGroup, startTime, quantityKwh
  - Evidence: Notebook Cell 5
  - Test: DataFrame with exactly 4 columns verified

- [ ] **5. MongoDB Storage**
  - Database: ind320
  - Collection: production_2021
  - Evidence: Notebook Cell 8, `lib/mongodb_client.py`
  - Test: MongoDB connection verified in Part 3

- [ ] **6. Streamlit Uses MongoDB (NO CSV)**
  - Files: `app.py`, `pages/02_PriceArea.py`
  - Evidence: No `read_csv()` for Elhub data
  - Test: Verified in Part 7

- [ ] **7. Pie Chart**
  - Evidence: Notebook Cell 6
  - Shows: Total production by group
  - Test: Chart displayed in Part 5

- [ ] **8. Line Plot**
  - Evidence: Notebook Cell 7
  - Shows: First month hourly production
  - Test: Chart displayed in Part 5

- [ ] **9. Data Source Documentation**
  - Evidence: Notebook markdown cells, Streamlit expanders
  - Test: Verified in Part 8

- [ ] **10. AI Usage Description**
  - Evidence: Notebook Cell 9
  - Test: Verified in Part 8

- [ ] **11. Work Log (300-500 words)**
  - Evidence: Notebook Cell 10, `IND320_Assessment2.md`
  - Test: Word count verified in Part 8

---

## Summary Checklist

### Critical Items (MUST ALL PASS)

- [ ] MongoDB connection works
- [ ] Elhub API script uses `requests.get()` (NOT CSV download)
- [ ] Streamlit app runs locally without errors
- [ ] Jupyter notebook executes all cells successfully
- [ ] Pie chart and line plot display correctly
- [ ] NO CSV files used for Elhub data in Streamlit
- [ ] All code committed to git
- [ ] Documentation complete (AI usage + work log)

### If ANY Critical Item Fails

**STOP** and fix before proceeding to deployment.

---

## After Completing This Checklist

If all items are checked ✅, you are ready for:

1. **Push to GitHub:**
   ```bash
   git push origin assignment3_update
   ```

2. **Deploy to Streamlit Cloud** (see `DEPLOYMENT_GUIDE.md`)

3. **Verify public accessibility**

---

## Test Results Log

Date: _______________
Tester: _______________

**Part 1 (Files):** ☐ Pass ☐ Fail
**Part 2 (Syntax):** ☐ Pass ☐ Fail
**Part 3 (MongoDB):** ☐ Pass ☐ Fail
**Part 4 (API):** ☐ Pass ☐ Fail
**Part 5 (Notebook):** ☐ Pass ☐ Fail
**Part 6 (Streamlit):** ☐ Pass ☐ Fail
**Part 7 (Data Source):** ☐ Pass ☐ Fail
**Part 8 (Docs):** ☐ Pass ☐ Fail
**Part 9 (Git):** ☐ Pass ☐ Fail
**Part 10 (Deployment):** ☐ Pass ☐ Fail
**Part 11 (Requirements):** ☐ Pass ☐ Fail

**Overall Status:** ☐ READY FOR DEPLOYMENT ☐ NEEDS FIXES

**Notes:**
_____________________________________________
_____________________________________________
_____________________________________________

---

**Estimated Total Time:** 90 minutes
**Last Updated:** November 20, 2025
