# IND320 Assessment 4 - Complete Overview and Implementation Guide

## Overview
Assessment 4 is the final part of a four-part project that builds a comprehensive energy data analytics portfolio. This assessment focuses on extending the existing Jupyter Notebook and Streamlit app with advanced features including interactive maps, snow drift calculations, meteorological correlations, and energy forecasting.

**Deliverables:**
1. Jupyter Notebook (local) with 300-500 word log and AI usage description
2. Streamlit app (deployed at https://[yourproject].streamlit.app/)
3. GitHub repository with all code
4. PDF export of Jupyter Notebook

**Subject to revisions before deadline, especially during first week**

---

## Project Goals

### Primary Goals
1. Extend existing data pipeline with 2022-2024 production data and 2021-2024 consumption data
2. Create interactive map visualization with GeoJSON overlays of Norwegian price areas
3. Implement snow drift calculations with wind rose visualizations
4. Build meteorological-energy correlation analysis tool
5. Develop SARIMAX-based energy forecasting system
6. Demonstrate AI tool usage throughout development
7. Document the entire development process

### Learning Objectives
- Work with spatial data (GeoJSON) and interactive maps
- Integrate multiple data sources (Elhub API, MongoDB, Cassandra, open-meteo API)
- Implement time series forecasting with SARIMAX
- Build user-friendly interactive dashboards
- Practice version control with feature branches
- Document code comprehensively

---

## Requirements Breakdown

### 1. General Requirements (Same as Part 3)

#### GitHub Workflow
- **DO NOT** push directly to main branch before peer review and teacher feedback
- Create and use a new feature branch for Assessment 4 updates
- Merge into main only after peer review and feedback are finished

#### Project Structure
All work results in:
1. **Jupyter Notebook** (local development platform)
   - Brief description of AI usage
   - 300-500 word log describing compulsory work (Jupyter Notebook and Streamlit experience)
   - Links to public GitHub repository and Streamlit app
   - Clear document headings for navigation
   - Well-commented code blocks (understandable and reproducible)
   - All code blocks must be run before PDF export (messages and plots shown)
   - Add .ipynb file to GitHub repository

2. **Streamlit App** (online deployment)
   - Running from https://[yourproject].streamlit.app/
   - Access data from MongoDB database and open-meteo.com API
   - Code must include relevant comments from Jupyter Notebook
   - Additional comments regarding Streamlit usage

---

### 2. Jupyter Notebook Tasks

#### 2.1 Production Data (2022-2024)
**Source:** Elhub API
**Metric:** `PRODUCTION_PER_GROUP_MBA_HOUR`
**Time Range:** All days and hours of years 2022-2024
**Coverage:** All Norwegian price areas

**Implementation:**
- Handle data same way as in Part 2
- Append new data after existing 2021 data
- Store in both:
  - Cassandra (using Spark - see updated installation advice if struggling)
  - MongoDB

#### 2.2 Consumption Data (2021-2024)
**Source:** Elhub API
**Metric:** `CONSUMPTION_PER_GROUP_MBA_HOUR`
**Time Range:** All days and hours of years 2021-2024
**Coverage:** All Norwegian price areas

**Implementation:**
- Use new tables in databases
- Same strategy as production data
- Store in both Cassandra and MongoDB

**Note:** If you have example data in MongoDB, it may need to be removed to make room for new data.

---

### 3. Streamlit App - New Elements

#### 3.1 Map and Selectors

**Map Implementation:**
- Use Plotly OR Folio map
- GeoJSON-based overlay of Norwegian Price areas (NO1 - NO5)

**GeoJSON Data Source:**
- URL: https://temakart.nve.no/tema/nettanlegg
- Search for "NVE Elspot områder"
- Select "ElSpot_områder"
- Select all areas
- Export to GeoJSON format
- Use EUREF 89 Geografisk (ETRS 89) 2d format

**Map Features:**
1. Show outlines of Price areas
2. Store clicked coordinates in the app
3. Mark clicked points in the plot
4. Highlight chosen Price area with different outline
5. **BONUS:** Display municipalities when magnified beyond natural threshold, price areas otherwise
   - GeoJSON data: http://kartkatalog.geonorge.no (EUREF 89 Geografisk ETRS 89 2d format)
   - Strategy: Plot both grids (municipality and price area), set minzoom/maxzoom to control visibility

**UI Considerations:**
- Before deciding structure, plan which new elements to include
- Use pen and paper, PowerPoint, or similar to organize content before coding
- Let menubar reflect changes with grouping, headers, or similar
- Possible structure: Common front page pointing to 2-3 main analysis pages with their own menus
- Consider color themes or other effects to emphasize which group is active
- User-friendliness: Some pages use main page selection, others use local selections (e.g., year, location)

#### 3.2 Energy Production/Consumption Visualization

**User Inputs:**
- Energy production/consumption group selector
- Time interval selector (in days)

**Visualization:**
- Color price areas transparently (choropleth style)
- Color intensity based on mean values over selected time interval
- Display for chosen production/consumption metric

#### 3.3 Snow Drift Calculation and Illustration

**Base Code:**
- Copy and edit relevant parts of supplied file `Snow_drift.py`

**Year Definition:**
- 1 year = July 1st (selected year) to June 30th (following year)

**Calculations:**
- Calculate snow drift per year for selected year range
- Plot results

**User Inputs:**
- Year range selector
- Use coordinates chosen on map (gracefully refuse to plot/calculate if no selection made)

**Visualizations:**
- Snow drift plot over selected years
- Corresponding wind rose (see Snow_drift.py)

**BONUS:**
- See bonus section for extra possibilities regarding monthly snow drift

#### 3.4 Meteorology and Energy Production Analysis

**Task:**
- Transform existing Sliding Window Correlation code into Streamlit equivalent
- Use Plotly graphics (or equivalent)

**Features:**
- Selectable lag parameter
- Selectable window length parameter
- One selector for meteorological properties
- One selector for energy production/consumption

**Deliverable:**
- After implementation, analyze the tool
- Play with controls and check for correlation changes in:
  - Normal conditions
  - After extreme weather events
- Report findings in Jupyter Notebook log

#### 3.5 Forecasting of Energy Production and Consumption

**Model:** SARIMAX (Seasonal AutoRegressive Integrated Moving Average with eXogenous variables)

**Interface Requirements:**
- All relevant SARIMAX parameters must be selectable
- User chooses timeframe for training data
- User chooses forecast horizon

**Functionality:**
- Forecast user-selected property from energy production/consumption
- Use dynamic forecasting
- Include any selected exogenous variables

**Visualization:**
- Plot forecast results
- Include confidence intervals

**BONUS:**
- See bonus section regarding weather properties

---

### 4. Bonus Content (Select at Least ONE)

You must implement **at least one** task from this list. Report in the log which one(s) you chose.

#### 4.1 Waiting Time Indicators
- Use progress bars, spinners, or similar to indicate work in progress
- Cache everything possible to improve performance

#### 4.2 Error Handling
- Incorporate checks for missing data connections (API and database)
- Handle NaN/missing values in data
- Catch errors and give useful feedback instead of crashing or cryptic error messages

#### 4.3 Map Page Enhancement
- Display municipalities when magnified beyond natural threshold
- Display price areas otherwise
- GeoJSON data: http://kartkatalog.geonorge.no (EUREF 89 Geografisk ETRS 89 2d)
- Possible strategy: Plot both grids, set minzoom/maxzoom for each to control visibility

#### 4.4 Snow Drift Enhancement
- Calculate monthly snow drift in addition to yearly
- Plot monthly and yearly snow drift together

#### 4.5 Forecasting Enhancement
- Add weather properties to list of exogenous variables
- Download when needed for forecasting

#### 4.6 Elevation Information
- open-meteo also has an elevation API
- Use to add elevation information to selected points in main map
- OR create separate elevation map

---

## Evaluation Criteria

### Assessment Process
The uploaded PDF/HTML, GitHub repository, and Streamlit app will be assessed according to the requirements above.

**Reviewers:**
1. One fellow student (peer review)
2. Liland or Kjæreng (instructor)

### Feedback
- TA/Teacher feedback will be short and instructive
- Focus on points of improvement and requirement fulfillment

### Final Grade
- Based on all four rounds of hand-ins seen as a whole
- Assessment 4 is the capstone that demonstrates mastery

---

## Optimal Implementation Strategy

### Phase 1: Planning and Setup (Week 1)
1. Create new Git branch for Assessment 4
2. Review existing codebase from Parts 1-3
3. Plan Streamlit app structure on paper/PowerPoint
4. Set up development environment
5. Test existing functionality

### Phase 2: Data Pipeline Extension (Week 1-2)
1. Implement Elhub API calls for production data (2022-2024)
2. Implement Elhub API calls for consumption data (2021-2024)
3. Update Cassandra database with Spark
4. Update MongoDB database
5. Verify data integrity
6. Document data pipeline in Jupyter Notebook

### Phase 3: Map Implementation (Week 2)
1. Download and prepare GeoJSON data for price areas
2. Choose mapping library (Plotly vs Folio)
3. Implement basic map with price area overlays
4. Add click functionality to store coordinates
5. Implement price area highlighting
6. Test map interactivity
7. (Optional) Add municipality layer for bonus

### Phase 4: Energy Visualization (Week 2-3)
1. Create UI selectors for energy groups and time intervals
2. Implement data aggregation for mean values
3. Create choropleth visualization
4. Connect to map component
5. Test with different time ranges and metrics

### Phase 5: Snow Drift Analysis (Week 3)
1. Study provided Snow_drift.py file
2. Adapt code for Streamlit
3. Implement year range selector
4. Connect to map coordinates
5. Implement validation (no selection = no plot)
6. Create snow drift plot
7. Add wind rose visualization
8. (Optional) Add monthly calculations for bonus

### Phase 6: Correlation Analysis (Week 3-4)
1. Review existing Sliding Window Correlation code
2. Convert to Streamlit with Plotly
3. Implement lag and window length selectors
4. Create meteorological property selector
5. Create energy property selector
6. Run analysis during normal and extreme weather periods
7. Document findings in Jupyter Notebook log

### Phase 7: Forecasting System (Week 4-5)
1. Research SARIMAX implementation in Python
2. Create parameter selection interface
3. Implement training data timeframe selector
4. Implement forecast horizon selector
5. Build SARIMAX model with dynamic forecasting
6. Add exogenous variable selection
7. Create visualization with confidence intervals
8. (Optional) Add weather properties as exogenous variables for bonus

### Phase 8: Bonus Feature (Week 5)
1. Choose at least one bonus task
2. Implement chosen feature(s)
3. Test thoroughly
4. Document in log which bonus feature(s) were implemented

### Phase 9: Documentation and Polish (Week 5-6)
1. Write comprehensive code comments
2. Add AI usage description to Jupyter Notebook
3. Write 300-500 word log covering:
   - Jupyter Notebook development process
   - Streamlit app development experience
   - Challenges and solutions
   - AI tool usage and impact
   - Bonus feature(s) implemented
4. Add clear headings for navigation
5. Add links to GitHub repository and Streamlit app
6. Run all Jupyter Notebook cells
7. Export to PDF
8. Review all requirements

### Phase 10: Testing and Deployment (Week 6)
1. Test all Streamlit app features end-to-end
2. Test with different user inputs
3. Verify error handling
4. Check mobile responsiveness
5. Deploy to Streamlit Cloud
6. Verify deployment works correctly
7. Test public URL

### Phase 11: Peer Review Preparation (Week 6)
1. Push all code to feature branch
2. Create pull request (DO NOT MERGE YET)
3. Prepare for peer review
4. Address peer review feedback
5. Address instructor feedback
6. Make necessary revisions

### Phase 12: Final Submission (Week 7)
1. Incorporate all feedback
2. Final testing
3. Merge feature branch to main
4. Verify GitHub repository is public and accessible
5. Verify Streamlit app is live
6. Submit PDF/HTML of Jupyter Notebook
7. Final review of all deliverables

---

## Checklist for Maximum Marks

### GitHub Repository
- [ ] New feature branch created (not main)
- [ ] All code pushed to feature branch before peer review
- [ ] .ipynb file included in repository
- [ ] All Python files well-commented
- [ ] Requirements.txt or environment.yml included
- [ ] README with project description
- [ ] Repository is public and accessible
- [ ] Merged to main only after all feedback incorporated

### Jupyter Notebook
- [ ] Brief description of AI usage included
- [ ] 300-500 word log describing compulsory work
- [ ] Links to public GitHub repository included
- [ ] Links to Streamlit app included
- [ ] Clear document headings for easy navigation
- [ ] All code blocks well-commented
- [ ] Code is understandable and reproducible
- [ ] All code blocks executed before export
- [ ] All plots and messages visible in export
- [ ] Exported to PDF format
- [ ] Correlation analysis findings documented
- [ ] Bonus feature selection documented

### Data Pipeline (Jupyter Notebook)
- [ ] Elhub API integration for production data (2022-2024)
- [ ] Elhub API integration for consumption data (2021-2024)
- [ ] Data stored in Cassandra using Spark
- [ ] Data stored in MongoDB
- [ ] New tables created (not overwriting old data)
- [ ] Data integrity verified
- [ ] Process documented

### Streamlit App - Map Component
- [ ] Plotly or Folio map implemented
- [ ] GeoJSON data for price areas (NO1-NO5) downloaded
- [ ] Price area outlines displayed
- [ ] Click functionality to store coordinates
- [ ] Clicked points marked on plot
- [ ] Selected price area highlighted differently
- [ ] Map is user-friendly and responsive

### Streamlit App - Energy Visualization
- [ ] Energy production/consumption group selector
- [ ] Time interval selector (in days)
- [ ] Choropleth coloring of price areas
- [ ] Colors represent mean values over time interval
- [ ] Visualization updates based on selections

### Streamlit App - Snow Drift
- [ ] Snow_drift.py code adapted for Streamlit
- [ ] Year defined as July 1 - June 30
- [ ] Year range selector implemented
- [ ] Coordinates from map used
- [ ] Graceful handling when no coordinates selected
- [ ] Snow drift calculation per year
- [ ] Snow drift plot displayed
- [ ] Wind rose visualization included

### Streamlit App - Meteorology Correlation
- [ ] Sliding Window Correlation converted to Streamlit
- [ ] Plotly graphics (or equivalent) used
- [ ] Lag parameter selector
- [ ] Window length parameter selector
- [ ] Meteorological property selector
- [ ] Energy production/consumption selector
- [ ] Analysis performed during normal conditions
- [ ] Analysis performed during/after extreme weather
- [ ] Findings reported in Jupyter Notebook log

### Streamlit App - Forecasting
- [ ] SARIMAX interface created
- [ ] All relevant parameters are selectable
- [ ] Training data timeframe selector
- [ ] Forecast horizon selector
- [ ] Forecast for user-selected energy property
- [ ] Dynamic forecasting implemented
- [ ] Exogenous variables selectable and included
- [ ] Results plotted
- [ ] Confidence intervals displayed

### Bonus Features (Select at least 1)
- [ ] Waiting time indicators (progress bars/spinners)
- [ ] Caching implemented where possible
- [ ] Error handling for missing connections
- [ ] Error handling for NaN/missing values
- [ ] Useful error messages (not crashing)
- [ ] Map municipalities at high zoom levels
- [ ] Monthly snow drift calculations
- [ ] Monthly and yearly snow drift plotted together
- [ ] Weather properties as exogenous variables in forecasting
- [ ] Elevation information from open-meteo API
- [ ] Bonus feature(s) documented in log

### Streamlit App - General
- [ ] App structure is well-organized
- [ ] Menubar reflects organization (grouping/headers)
- [ ] Navigation is intuitive
- [ ] Color themes or visual cues for different sections
- [ ] Mix of main page and local selections as appropriate
- [ ] All comments from Jupyter Notebook included
- [ ] Additional Streamlit-specific comments added
- [ ] App deployed successfully
- [ ] Public URL accessible: https://[yourproject].streamlit.app/
- [ ] App connects to MongoDB successfully
- [ ] App connects to open-meteo API successfully
- [ ] App is responsive and user-friendly

### Code Quality
- [ ] All code is well-commented
- [ ] Comments explain the "why" not just the "what"
- [ ] Code is modular and reusable
- [ ] No hardcoded values where variables should be used
- [ ] Consistent naming conventions
- [ ] Error handling throughout
- [ ] Code follows Python best practices

### Testing
- [ ] All features tested individually
- [ ] End-to-end testing completed
- [ ] Tested with edge cases
- [ ] Tested with invalid inputs
- [ ] Mobile responsiveness checked
- [ ] Different browsers tested
- [ ] API connection failures handled
- [ ] Database connection failures handled

### Documentation
- [ ] Development process documented in log
- [ ] Challenges and solutions described
- [ ] AI tool usage clearly described
- [ ] All external data sources cited
- [ ] All libraries and tools listed
- [ ] Instructions for running locally (if applicable)

### Submission
- [ ] Peer review completed
- [ ] Instructor feedback addressed
- [ ] All revisions completed
- [ ] Feature branch merged to main
- [ ] PDF of Jupyter Notebook submitted
- [ ] All deliverables double-checked
- [ ] Submission deadline met

---

## Tips for Achieving Best Marks

### 1. Start Early
- Subject to revisions especially in first week
- Starting early allows time to adapt to changes
- Complex features like forecasting need iteration time

### 2. Plan Before Coding
- Sketch Streamlit app structure on paper/PowerPoint first
- Identify which features belong together
- Design navigation flow before implementation
- Consider user experience throughout

### 3. Document As You Go
- Write comments while coding, not after
- Keep notes for the 300-500 word log
- Document AI usage immediately when used
- Track challenges and solutions in real-time

### 4. Test Continuously
- Test each feature as implemented
- Don't wait until the end for testing
- Fix bugs immediately while context is fresh
- Test edge cases early

### 5. Use Version Control Properly
- Commit frequently with descriptive messages
- Use feature branch as required
- Don't merge to main until after feedback
- Keep commits atomic and focused

### 6. Leverage AI Tools Appropriately
- Use AI for code suggestions and debugging
- Document every instance of AI usage
- Review and understand AI-generated code
- Don't blindly copy AI suggestions

### 7. Focus on User Experience
- Make the app intuitive and easy to navigate
- Provide clear feedback for user actions
- Handle errors gracefully
- Use visual cues (colors, grouping, headers)
- Test with someone unfamiliar with the project

### 8. Implement Bonus Features Strategically
- Choose bonus features that complement your strengths
- Error handling is highly valuable for any app
- Caching/progress indicators improve user experience significantly
- Document clearly which bonus features were implemented

### 9. Code Quality Matters
- Write clean, readable code
- Follow Python conventions (PEP 8)
- Use meaningful variable names
- Keep functions focused and modular
- Remove dead code and debug statements

### 10. Communication is Key
- Write clear, concise comments
- The 300-500 word log should tell a story
- Link code to requirements explicitly
- Make it easy for reviewers to find features

---

## Common Pitfalls to Avoid

1. **Pushing to main before peer review** - Explicitly forbidden, will cause issues
2. **Insufficient documentation** - Code without context is hard to evaluate
3. **Not running all Jupyter cells before export** - Results in incomplete PDF
4. **Hardcoding values** - Makes code inflexible and hard to maintain
5. **Ignoring error handling** - App crashes create poor user experience
6. **Poor app structure** - Confusing navigation loses marks
7. **Missing AI usage description** - Required component, don't forget
8. **Not selecting coordinates gracefully** - Must handle missing selections
9. **Forgetting to implement at least one bonus** - Mandatory requirement
10. **Last-minute deployment issues** - Deploy early to catch problems
11. **Not testing with real data** - Assumptions may not match reality
12. **Skipping peer review feedback** - Valuable improvement opportunity

---

## Resources and References

### Data Sources
- Elhub API: Production and consumption data
- NVE GeoJSON: https://temakart.nve.no/tema/nettanlegg
- Geonorge: http://kartkatalog.geonorge.no
- Open-Meteo API: https://open-meteo.com/

### Libraries and Tools
- **Streamlit**: Web app framework
- **Plotly / Folium**: Interactive mapping
- **SARIMAX**: Time series forecasting (statsmodels)
- **Spark**: Big data processing with Cassandra
- **MongoDB**: NoSQL database
- **Cassandra**: Distributed database
- **Pandas**: Data manipulation
- **Numpy**: Numerical computing

### Coordinate Systems
- EUREF 89 Geografisk (ETRS 89) 2d format for GeoJSON data

---

## Timeline Recommendation

| Week | Focus | Key Deliverables |
|------|-------|------------------|
| 1 | Planning & Data Pipeline | Branch created, data pipeline extended |
| 2 | Map Implementation | Interactive map with price areas |
| 3 | Snow Drift & Energy Viz | Snow drift calculator, energy choropleth |
| 4 | Correlation Analysis | Sliding window correlation in Streamlit |
| 5 | Forecasting & Bonus | SARIMAX interface, bonus feature(s) |
| 6 | Documentation & Testing | Complete log, PDF export, deployment |
| 7 | Review & Submission | Feedback incorporation, final submission |

**Note:** Adjust timeline based on your schedule and assignment release date.

---

## Questions to Ask Instructor (If Unclear)

1. Specific format requirements for the 300-500 word log?
2. Preferred approach for handling existing MongoDB data?
3. Clarification on "relevant parts" of Snow_drift.py to copy?
4. Expected depth of correlation analysis findings?
5. Specific SARIMAX parameters that must be exposed to users?
6. Deadline for peer review completion?
7. Format for final submission (PDF only or HTML acceptable)?

---

## Success Criteria Summary

To achieve the best marks, you must:

1. Complete ALL compulsory features correctly
2. Implement AT LEAST ONE bonus feature
3. Use proper GitHub workflow (feature branch, no main until approved)
4. Provide comprehensive documentation (comments, log, AI usage)
5. Create a user-friendly, well-structured Streamlit app
6. Successfully deploy all components (Jupyter, GitHub, Streamlit)
7. Handle errors gracefully throughout the app
8. Test thoroughly and demonstrate quality code
9. Incorporate peer and instructor feedback
10. Submit all deliverables on time

---

**This assessment builds on Parts 1-3 and represents the capstone of your IND320 portfolio. Take time to plan, implement carefully, document thoroughly, and polish your work. Good luck!**
