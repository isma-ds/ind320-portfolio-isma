# Instructor Feedback Analysis - Critical Issues to Fix

## OUTCOME: Assessment 2 FAILED - Must Fix in Assessment 3

Instructor: Kristian
Date: Received before Assessment 4
Status: **MUST FIX ALL ISSUES**

---

## ASSESSMENT 2 - CRITICAL ERRORS

### ❌ ERROR 1: CSV Download Instead of API
**What Client Did Wrong:**
```python
DATA_URL = "https://data.elhub.no/download/production_per_group_mba_hour/production_per_group_mba_hour-all-en-0000-00-00.csv"
# This is WRONG - downloading CSV file directly
```

**What Should Be Done:**
```python
# Use PROPER API endpoint
url = "https://api.elhub.no/energy-data/v0/price-areas"
params = {"dataset": "PRODUCTION_PER_GROUP_MBA_HOUR"}
response = requests.get(url, params=params)
data = response.json()  # JSON response, NOT CSV
```

**Correct API URL:**
- ✅ https://api.elhub.no/energy-data-api/price-areas
- ✅ Returns JSON data
- ❌ NOT a file download

---

### ❌ ERROR 2: Cassandra Failing
**Client's Excuse:** "Docker not supported on my laptop hardware"

**Instructor's Response:**
- This should have been reported in mid-September
- Cassandra is directly installable on Windows/MacOS (no Docker needed)
- MacOS 12.7+ has unofficial binaries: https://gist.github.com/franklinyu/5e0bb9d6c0d873f33c78415dd2ea4138

**FIX REQUIRED:**
- Install Cassandra without Docker
- OR properly document why it's impossible
- OR use Docker Desktop (which we already have working!)

**GOOD NEWS:** We already have `docker-compose.yml` working from Assessment 4!

---

### ❌ ERROR 3: MongoDB NOT Used in Streamlit
**What Client Did Wrong:**
- Uploaded data to MongoDB in Jupyter Notebook ✓
- But Streamlit app downloads fresh CSV files ✗

**Requirement (from assignment):**
> "Establish a connection with your MongoDB database. When running this at streamlit.io, remember to copy your secrets to the webpage instead of exposing them on GitHub."

**FIX REQUIRED:**
- Streamlit app MUST connect to MongoDB
- NO CSV downloads in Streamlit
- Use st.secrets for MongoDB URI
- All data must come from MongoDB

---

### ❌ ERROR 4: Streamlit App Not Accessible
**Link Provided:** https://ind320-portfolio-isma-wqi6qhsb5pchqddfejkmkj.streamlit.app/Production

**Problem:** Link doesn't work (app is private or wrong URL)

**FIX REQUIRED:**
- Make app PUBLIC
- Verify correct URL
- Test from logged-out browser

---

## STREAMLIT PAGE-SPECIFIC ERRORS

### ❌ Page 2: Missing LineChartColumn()
**Requirement from Part 1:**
> "A table showing the imported data. Use the row-wise LineChartColumn() to display the first month of the data series."

**FIX REQUIRED:**
- Add LineChartColumn() to Page 2
- Show first month of data series
- One row per data column

---

### ❌ Page 3: Wrong Slider Type
**What Client Has:** "Days back" slider
**What's Required:** Month selector slider

**Original Requirement:**
> "A selection slider (st.select_slider) to select a subset of the months. Defaults should be the first month."

**FIX REQUIRED:**
- Replace "days back" slider
- Use st.select_slider
- Select month range
- Default: first month

---

### ❌ Page 4: Extra "Unspecified" in Labels
**Problem:** All production groups have extra "unspecified" part in their labels

**Example:**
- "Hydro - unspecified"
- "Wind - unspecified"

**FIX REQUIRED:**
- Clean up labels
- Should be just: "Hydro", "Wind", "Thermal", "Solar"
- Check data cleaning in MongoDB insert

---

## ASSESSMENT 3 - ADDITIONAL ERRORS

### ❌ NOT Merged to Main Branch
**Problem:** Parts 2 and 3 are in separate branches

**Requirement:**
> "You need to merge part 3 into the main branch of the repository so it is assessable."

**FIX REQUIRED:**
- Merge Assessment 3 into main branch
- Ensure all work is visible on main

---

### ❌ STL Analysis: Single Plot Instead of Four
**What Client Has:** STL plotted in single plot
**What's Required:** Four separate parts

**Correct STL Components (4 plots):**
1. Original data
2. Trend component
3. Seasonal component
4. Residual component

**FIX REQUIRED:**
- Split into 4 subplots
- Follow lecture format

---

### ❌ SPC Analysis: Straight Lines Instead of Curved
**What Client Has:** Straight lines for control limits
**What's Required:** Curved control limits

**Problem:** Missing difference between:
- Raw data
- High-pass filtered data

**FIX REQUIRED:**
- Implement proper high-pass filtering
- Calculate curved control limits
- Show both raw and filtered

---

### ❌ LOF Placement Wrong
**What Client Has:** LOF below SPC
**What's Required:** LOF should be in a TAB

**FIX REQUIRED:**
- Use st.tabs
- Put LOF in separate tab
- Not stacked below SPC

---

### ❌ Duplicate/Faulty Menu
**Problem:** Two menus on front page, lower one partly faulty

**FIX REQUIRED:**
- Remove duplicate menu
- Fix navigation issues
- Clean up front page

---

## INSTRUCTOR'S PATH FORWARD

### Quote:
> "The easiest way forward is to correct all the above, but do it in part 3 of the assignment."

### Strategy:
1. ✅ Fix ALL Assessment 2 issues
2. ✅ Implement fixes in Assessment 3 branch
3. ✅ Fix Assessment 3 specific issues
4. ✅ Merge Assessment 3 to main branch
5. ✅ Submit corrected version

---

## PRIORITY FIX LIST

### HIGH PRIORITY (Blocking):
1. **Use API instead of CSV download** ⚠️ CRITICAL
2. **MongoDB in Streamlit** ⚠️ CRITICAL
3. **Fix Streamlit app accessibility** ⚠️ CRITICAL
4. **Merge to main branch** ⚠️ CRITICAL

### MEDIUM PRIORITY (Required for pass):
5. Cassandra working (or proper documentation)
6. Page 2: Add LineChartColumn()
7. Page 3: Fix slider type
8. Page 4: Clean labels

### ASSESSMENT 3 FIXES:
9. STL: 4 separate plots
10. SPC: Curved control limits
11. LOF: Move to tab
12. Front page: Remove duplicate menu

---

## TECHNICAL FIXES NEEDED

### 1. API Usage (Jupyter Notebook)
```python
# WRONG - DO NOT USE
DATA_URL = "https://data.elhub.no/download/...csv"

# CORRECT - USE THIS
import requests

url = "https://api.elhub.no/energy-data/v0/price-areas"
params = {
    "dataset": "PRODUCTION_PER_GROUP_MBA_HOUR",
    "startTime": "2021-01-01T00:00:00Z",
    "endTime": "2021-12-31T23:59:59Z"
}

response = requests.get(url, params=params)
data = response.json()

# Extract from JSON response
production_data = data['data'][0]['attributes']['productionPerGroupMbaHour']
df = pd.DataFrame(production_data)
```

### 2. MongoDB in Streamlit
```python
# Add to all Streamlit pages that need data

from pymongo import MongoClient

@st.cache_resource
def get_mongo_client():
    mongo_uri = st.secrets["MONGO_URI"]
    return MongoClient(mongo_uri)

@st.cache_data(ttl=3600)
def load_data_from_mongodb():
    client = get_mongo_client()
    db = client['ind320']
    collection = db['production_2021']
    df = pd.DataFrame(list(collection.find({}, {'_id': 0})))
    return df

# Use it
df = load_data_from_mongodb()
# NO CSV DOWNLOADS!
```

### 3. Cassandra Setup
```bash
# We already have docker-compose.yml from Assessment 4!
cd "C:\Users\hisha\Documents\Aoun Assignment\ind320-portfolio-isma"

# Start Cassandra
docker-compose up -d

# Wait 2 minutes, then initialize
docker exec -i cassandra1 cqlsh < cassandra-init/init.cql
```

### 4. Clean Production Labels
```python
# When inserting to MongoDB, clean the labels
df['productionGroup'] = df['productionGroup'].str.replace(' - unspecified', '')
df['productionGroup'] = df['productionGroup'].str.strip()
```

---

## NEXT STEPS

### Step 1: Review Existing Code
Check what's on the branches:
- `origin/assignment2` - Failed version
- `origin/assignment3_update` - Has Assessment 3 work
- `origin/assessment4` - Has our advanced work

### Step 2: Create Fix Branch
```bash
# Start from assignment3_update
git checkout assignment3_update
git checkout -b assignment3_complete
```

### Step 3: Apply Fixes
Work through priority list systematically

### Step 4: Test Everything
- Test locally
- Deploy to Streamlit
- Verify app is PUBLIC
- Test from logged-out browser

### Step 5: Merge to Main
```bash
git checkout main
git merge assignment3_complete
git push origin main
```

---

## QUESTIONS TO ANSWER FIRST

1. **Which branch has the most recent working code?**
   - assignment2?
   - assignment3_update?
   - Something else?

2. **Do you want to:**
   - Fix existing code?
   - Start fresh with correct approach?
   - Hybrid (use some existing, fix critical parts)?

3. **Priority:**
   - Fix Assessment 2 only (minimum to pass)?
   - Fix both Assessment 2 + 3 (complete solution)?

---

## GOOD NEWS

✅ We already have working solutions from Assessment 4:
- Real Elhub API integration ✓
- Cassandra Docker setup ✓
- MongoDB connection ✓
- Clean data pipeline ✓

We can backport these fixes to Assessment 3!

---

**Let me know which branch to check first, and I'll help fix ALL these issues!**
