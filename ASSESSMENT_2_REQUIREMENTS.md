# Assessment 2 - Requirements

## CRITICAL: Branch Management
- **DO NOT push to main branch before peer review**
- Create and use NEW BRANCH for updates
- Merge to main AFTER peer review and feedback complete

## General Requirements

### Jupyter Notebook
- Run locally
- Brief description of AI usage
- 300-500 word log (Jupyter + Streamlit)
- Links to GitHub repository and Streamlit app
- Clear document headings
- Well-commented code blocks
- Run all code blocks before PDF export
- Add .ipynb file to GitHub

### Streamlit App
- Running from https://[yourproject].streamlit.app/
- Access CSV data AND MongoDB database
- Code on GitHub with comments

## Tasks

### 1. Accounts and Repositories
- [x] Reuse account, repository, Streamlit app from Assessment 1
- [ ] Push to TEMPORARY GitHub branch (not main)
- [ ] Merge after peer review complete

### 2. Local Database: Cassandra
- [ ] Set up Cassandra (as described in book)
- [ ] Set up Spark
- [ ] Test Spark-Cassandra connection works
- [ ] Access from Jupyter Notebook
- [ ] Store API data in Cassandra

### 3. Remote Database: MongoDB
- [x] Prepare MongoDB account at mongodb.com
- [ ] Test data manipulation from Python
- [ ] Store trimmed/curated/prepared data (from Spark filtering)
- [ ] Access directly from Streamlit app

### 4. API: Elhub
- [ ] Familiarize with https://api.elhub.no
- [ ] Understand time encoding
- [ ] Handle summer/winter time transitions
- [ ] Know time period limitations per request
- [ ] Know dataset differences

### 5. Jupyter Notebook Tasks

**CRITICAL DATA REQUIREMENTS:**
- [ ] Use Elhub API: PRODUCTION_PER_GROUP_MBA_HOUR
- [ ] Year: **2021 ONLY**
- [ ] All price areas
- [ ] All days and hours

**WORKFLOW:**
1. [ ] Retrieve 2021 production data from Elhub API
2. [ ] Extract only `productionPerGroupMbaHour` list
3. [ ] Convert to DataFrame
4. [ ] Insert data into **Cassandra** using **Spark**
5. [ ] Use **Spark** to extract columns from Cassandra:
   - priceArea
   - productionGroup
   - startTime
   - quantityKwh
6. [ ] Create plots:
   - **Pie chart:** Total production for chosen price area (one piece per production group)
   - **Line plot:** First month, chosen price area, separate lines per production group
7. [ ] Insert Spark-extracted data into **MongoDB**
8. [ ] Fill in log and AI usage (300-500 words)

### 6. Streamlit App Updates

**Page Organization:**
- [ ] If page 4 has content to keep, move to new page 5
- [ ] Establish MongoDB connection
- [ ] Use secrets at streamlit.io (DON'T expose on GitHub)

**Page 4 Layout:**
- [ ] Split into two columns (st.columns)

**Left Column:**
- [ ] Radio buttons (st.radio) to select price area
- [ ] Display pie chart (like Jupyter Notebook)

**Right Column:**
- [ ] Pills (st.pills) to select production groups
- [ ] Selector (your choice) for month selection
- [ ] Combine: price area + production group(s) + month
- [ ] Display line plot (like Jupyter Notebook, but any month)

**Below Columns:**
- [ ] Expander (st.expander)
- [ ] Brief documentation of data source

## Data Flow Architecture

```
Elhub API (2021 production data)
    ↓
Extract productionPerGroupMbaHour
    ↓
Convert to DataFrame
    ↓
INSERT → Cassandra (via Spark)
    ↓
EXTRACT (Spark) → 4 columns: priceArea, productionGroup, startTime, quantityKwh
    ↓
INSERT → MongoDB
    ↓
Streamlit App reads from MongoDB
```

## Key Points

1. **Cassandra is LOCAL** - accessed from Jupyter only
2. **MongoDB is REMOTE** - accessed from both Jupyter and Streamlit
3. **Spark is required** - for Cassandra operations
4. **Year 2021 only** - for this assessment
5. **Production data only** - not consumption

## Evaluation
- PDF upload
- GitHub repository (on temporary branch initially)
- Streamlit app
- Peer review
- Teacher feedback
- Part of overall course evaluation

## Common Mistakes to Avoid
- ❌ Pushing to main before peer review
- ❌ Using wrong year (must be 2021)
- ❌ Using consumption instead of production
- ❌ Skipping Spark (must use Spark for Cassandra)
- ❌ Not filtering to 4 required columns
- ❌ Exposing MongoDB secrets on GitHub
