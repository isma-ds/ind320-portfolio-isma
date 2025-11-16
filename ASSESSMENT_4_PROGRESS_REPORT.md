# Assessment 4 - Progress Report

## Date: 2025-11-16

---

## CRITICAL ANSWERS TO YOUR QUESTIONS

### 1. Is it difficult to retrieve Elhub API credentials?

**Short Answer:** The assessment REQUIRES Elhub API access, BUT your previous assignments used 100% synthetic data. You need to ask your client.

**Details:**
- Assessment 4 explicitly states: "Use the Elhub API to retrieve hourly production data..."
- However, Assignment 2 notebook shows NO real Elhub integration
- Instead, it created fake/synthetic data with np.random
- This means either:
  - The client doesn't have API access (most likely)
  - The instructor provides credentials during the course
  - Elhub API requires special registration/approval

**What to tell your client:**
> "I need the Elhub API credentials to fetch real production/consumption data for 2021-2024. Your previous assignments used synthetic data. Please provide:
> 1. Elhub API credentials (username/password/token)
> 2. OR confirm I should continue generating synthetic data
> 3. OR provide an alternative data source"

---

### 2. Is Cassandra ACTUALLY required? (Reviewed assessment carefully)

**Short Answer:** YES, Cassandra is EXPLICITLY REQUIRED in the assessment.

**Evidence from Assessment:**
The requirement clearly states:
> "Handle these data the same way as in part 2 of the project, appending the new data after the 2021 data, **both in Cassandra (using Spark** - see updated advice in the installation page if you struggle) **and MongoDB.**"

**BUT - Reality from Assignment 2:**
Assignment 2 notebook says:
> "This notebook replaces the Astra Cassandra setup with a local simulation using Spark, Pandas, and cassandra-driver, due to authentication limitations in the Astra environment"

**Translation:**
- Assessment says: Use BOTH Cassandra AND MongoDB
- Assignment 2 reality: Cassandra was NEVER actually set up, only simulated

**Your Options:**

**Option A: Continue Simulation (Easiest)**
- Continue the simulation approach from Assignment 2
- Use Spark DataFrames to "simulate" Cassandra
- Actually store everything in MongoDB
- Document clearly what you did

**Option B: Set Up Real Cassandra**
- Set up Astra DB (free tier)
- OR install local Cassandra
- Configure properly with Spark
- This takes significant time/effort

**Option C: Ask Client for Clarification**
Ask: "Assignment 2 simulated Cassandra due to authentication issues. For Assessment 4, should I:
1. Continue simulation?
2. Set up real Cassandra/Astra DB?
3. Use MongoDB only?"

**My Recommendation:** Option A (continue simulation) unless client explicitly needs real Cassandra.

---

### 3. What is Snow Drift and its purpose?

**Snow Drift = Snow accumulation calculation due to wind**

**Scientific Explanation:**
- When wind blows over snow, it causes snow to move from one location to another
- This creates "drifts" - areas where snow accumulates more than where it originally fell
- Critical for Norway because it affects:
  - Hydroelectric power (snow melt = water for power)
  - Infrastructure planning
  - Avalanche risk assessment

**In this Assessment:**
You'll implement a tool that:
1. Takes a location (coordinates from map click)
2. Uses meteorological data (wind speed, direction, temperature, precipitation)
3. Calculates how much snow accumulates there per year
4. Displays wind rose diagram (shows where wind comes from)
5. Plots snow drift over time

**The Snow_drift.py File:**
- Contains pre-written physics formulas for snow drift
- You'll adapt it for Streamlit interface
- Without it, you'd need to research snow physics and implement from scratch

**Formula includes factors like:**
- Wind speed and direction
- Temperature (affects snow cohesion)
- Precipitation (snowfall amount)
- Terrain effects

**Year Definition for this assignment:**
- 1 year = July 1 (start) to June 30 (end)
- This matches snow season in Norway

**Tell your client:**
> "I need the Snow_drift.py file that should have been provided with Assessment 4 materials. It contains the snow drift calculation formulas I need to adapt for Streamlit. Without it, I'll need to research and implement snow physics calculations from scratch, which will take significant extra time."

---

## COMPLETED TASKS (Non-Blocking Work)

### Task 1: Created Assessment 4 Branch ✓
- **Branch Name:** `assessment4`
- **Based On:** `origin/assignment3_update` (most recent complete work)
- **Status:** Ready for development

### Task 2: Downloaded GeoJSON Data ✓
- **File:** `geojson_data/elspot_areas.geojson`
- **Size:** 2.1 MB (detailed polygon boundaries)
- **Content:** All 5 Norwegian Price Areas
  - NO1 (Eastern Norway)
  - NO2 (Southern Norway)
  - NO3 (Central Norway)
  - NO4 (Northern Norway)
  - NO5 (Western Norway)
- **Format:** GeoJSON with polygon geometries
- **Coordinate System:** Compatible with mapping libraries

---

## NEXT STEPS (Non-Blocking Tasks In Progress)

I'm now working on:

### 1. Generating Synthetic Data
Since you don't have Elhub API credentials (yet), I'll create synthetic data matching Assignment 2 format:

**Production Data (2022-2024):**
- 5 price areas (NO1-NO5)
- 4 production groups (HYDRO, THERMAL, WIND, SOLAR)
- Hourly data for 3 years
- Realistic patterns (seasonal variations, day/night cycles)

**Consumption Data (2021-2024):**
- Same structure as production
- Different value ranges (consumption vs production)
- 4 years of data

### 2. Setting Up Jupyter Notebook Structure
- Create `notebooks/IND320_Assignment4.ipynb`
- Template for 300-500 word log
- AI usage description section
- Links to GitHub and Streamlit

### 3. Planning Streamlit App Structure
- Design navigation (map, energy viz, snow drift, correlation, forecasting)
- Plan page organization
- UI/UX considerations

---

## WHAT YOUR CLIENT MUST PROVIDE

### CRITICAL (Blockers if not provided):

1. **Elhub API Credentials OR confirmation to use synthetic data**
   - Without this, I cannot proceed with real data
   - Synthetic data is fallback option

2. **Snow_drift.py file**
   - Should have been provided with assignment materials
   - Contains snow drift calculation formulas
   - Without it, significant extra work needed

3. **Cassandra decision:**
   - Continue simulation from Assignment 2?
   - Set up real Cassandra?
   - Use MongoDB only?

### OPTIONAL (Nice to have):

4. **Any specific preferences for implementation**
   - Map library choice (Plotly vs Folium)
   - Color schemes
   - Bonus features to prioritize

5. **Deadline confirmation** (you said not to worry, but good to know)

---

## CURRENT PROJECT STATE

### What EXISTS and WORKS:
✓ MongoDB Atlas with credentials
✓ 2021 synthetic production data in MongoDB
✓ Streamlit app framework from Assignment 3
✓ Open-Meteo API integration (weather data)
✓ Python environment with required packages
✓ GitHub repository with proper structure
✓ GeoJSON data for Norwegian price areas

### What DOESN'T EXIST (Blockers):
✗ Elhub API credentials
✗ Real production/consumption data (all synthetic)
✗ Cassandra database (only simulated in A2)
✗ 2021 consumption data
✗ 2022-2024 data of any kind
✗ Snow_drift.py file

### What I'M CREATING NOW:
⚙ Synthetic 2021-2024 consumption data
⚙ Synthetic 2022-2024 production data
⚙ Assessment 4 Jupyter Notebook structure
⚙ Streamlit app navigation plan

---

## RECOMMENDED APPROACH

### Path Forward (Recommended):

**Phase 1: Use Synthetic Data (NOW)**
- I'll generate realistic synthetic data for all missing years
- Store in MongoDB (existing infrastructure)
- Continue Cassandra simulation from Assignment 2
- Get everything working end-to-end

**Phase 2: Swap to Real Data (IF client gets API credentials)**
- Replace synthetic data with real Elhub data
- Everything else stays the same
- Minimal code changes needed

**Why this approach:**
- Unblocks development immediately
- Assignment 2 already used synthetic data
- Can swap data source later without major rework
- Demonstrates all required features

### Alternative Path (If Client Insists on Real Data First):
- WAIT for Elhub API credentials
- Development stalls until received
- Risk missing deadlines
- Not recommended given past approach

---

## SUMMARY FOR YOUR CLIENT DISCUSSION

**Message to send your client:**

> "I've analyzed Assignment 4 requirements and your previous work (Assignments 1-3). Here's what I found:
>
> **Good News:**
> - MongoDB is configured and working
> - I have all Assignment 3 code as foundation
> - I've downloaded Norwegian price area maps (GeoJSON)
> - I've created Assessment 4 development branch
>
> **Questions I need answered:**
>
> 1. **Elhub API Access:** Assessment 4 requires fetching real energy data via Elhub API. Your Assignment 2 used synthetic data. Should I:
>    - Get Elhub API credentials from you/instructor?
>    - Continue with synthetic data generation?
>    - Use alternative data source?
>
> 2. **Cassandra Database:** Assessment 4 requires Cassandra + Spark, but Assignment 2 only simulated it due to 'authentication limitations.' Should I:
>    - Continue simulation approach?
>    - Set up real Cassandra/Astra DB?
>    - Use MongoDB only?
>
> 3. **Snow_drift.py File:** Assessment requires adapting a 'supplied file Snow_drift.py' for snow drift calculations. I don't have this file. Can you provide it?
>
> **My Recommendation:**
> Let me proceed with synthetic data (like Assignment 2) and simulated Cassandra while you get these answers. This keeps the project moving. We can swap to real data later if you get API access.
>
> **Timeline:**
> I can have the full assessment completed within 6 weeks using synthetic data, or add 1-2 weeks if waiting for real API access.
>
> Please advise how to proceed."

---

## FILES CREATED SO FAR

1. `ASSESSMENT_4_OVERVIEW.md` - Complete requirements breakdown and implementation guide
2. `ASSESSMENT_4_PREREQUISITES_ANALYSIS.md` - Detailed analysis of what exists vs what's needed
3. `ASSESSMENT_4_PROGRESS_REPORT.md` - This file
4. `geojson_data/elspot_areas.geojson` - Norwegian price area boundaries
5. Git branch: `assessment4` - Ready for development

---

## NEXT IMMEDIATE TASKS (Once You Approve)

1. Generate synthetic 2021 consumption data
2. Generate synthetic 2022-2024 production data
3. Generate synthetic 2022-2024 consumption data
4. Store all data in MongoDB
5. Create Assessment 4 Jupyter Notebook template
6. Begin Streamlit app enhancements

**I'm ready to proceed with these tasks. Should I continue with synthetic data approach?**
