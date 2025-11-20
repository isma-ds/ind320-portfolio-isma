# Assessment 1 - Requirements

## General Requirements

### Jupyter Notebook
- Run locally on your computer
- Brief description of AI usage
- 300-500 word log describing work (Jupyter + Streamlit)
- Links to GitHub repository and Streamlit app
- Clear document headings for navigation
- Well-commented code blocks
- Run all code blocks before PDF export
- Add .ipynb file to GitHub

### Streamlit App
- Running from https://[yourproject].streamlit.app/
- Online version accessing CSV data
- Code hosted on GitHub with comments
- Unique address including GitHub username

## Tasks

### 1. GitHub and Streamlit.app Accounts
- [x] Create GitHub account and public repository
- [x] Include username in repository name
- [x] Login to share.streamlit.io
- [x] Create minimum working Streamlit app
- [x] Push to GitHub
- [x] Ensure works at streamlit.app

### 2. Jupyter Notebook
- [ ] Read CSV file using Pandas
- [ ] Print contents in relevant way
- [ ] Plot each column separately
- [ ] Plot all columns together (consider different scales)
- [ ] Fill in log and AI usage

### 3. Streamlit App
- [x] requirements.txt for dependencies
- [x] Four pages with headers
- [x] Front page with sidebar navigation
- [ ] **Page 2:**
  - Table showing imported data
  - LineChartColumn() for first month
  - One row per data column
- [ ] **Page 3:**
  - Plot of imported data
  - Header, axis titles, formatting
  - Dropdown menu (st.selectbox) for column selection
  - Selection slider (st.select_slider) for month subset
  - Default: first month
- [x] Read from local CSV (open-meteo-subset.csv)
- [x] Use caching for speed

## Data File
- open-meteo-subset.csv (from Canvas)

## Evaluation
- PDF upload
- GitHub repository
- Streamlit app
- Peer review by fellow student
- Teacher feedback (Liland or Kjæreng)
- All four assessments evaluated as a whole
