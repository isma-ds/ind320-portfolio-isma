# 🧪 Testing Guide - Assessment 3

## ✅ **Streamlit App is COMPLETE and Ready to Test!**

---

## 🚀 **How to Test Assessment 3**

### **Option 1: Test Streamlit App Locally** (Recommended First)

#### **Step 1: Navigate to Project**
```bash
cd /home/hishamtariq/aoun_assessment/ind320-portfolio-isma
```

#### **Step 2: Run Streamlit**
```bash
streamlit run app.py
```

#### **Step 3: Test Each Page**

**Page 1: Home**
- ✅ Check MongoDB connection status
- ✅ Verify document count displays

**Page 2: Price Area Selector** (Was Page 4 in A2)
- ✅ Select different price areas (NO1-NO5)
- ✅ Verify pie chart updates
- ✅ Select different production groups
- ✅ Select different months
- ✅ Verify line chart updates

**Page 3: Analysis A - STL & Spectrogram** (NEW!)
- ✅ **Tab 1: STL Decomposition**
  - Select price area
  - Select production group
  - Adjust period slider
  - Adjust seasonal smoother
  - Adjust trend smoother
  - Toggle robust checkbox
  - Verify plot displays all components
- ✅ **Tab 2: Spectrogram**
  - Adjust window length
  - Adjust overlap slider
  - Toggle polar view
  - Verify spectrogram displays

**Page 4: Data Table** (Was Page 2 in A1)
- ✅ Verify table displays with line chart column
- ✅ Check first month data preview

**Page 5: Plot Page** (Was Page 3 in A1)
- ✅ Select different columns
- ✅ Use month slider
- ✅ Verify plot updates

**Page 6: Analysis B - SPC & LOF** (NEW!)
- ✅ **Tab 1: Temperature Outliers (SPC)**
  - Adjust DCT cutoff slider
  - Adjust k-sigma threshold
  - Verify scatter plot shows outliers in red
  - Check metric cards (Total, Percentage, MAD)
  - Expand "View Outlier Details"
- ✅ **Tab 2: Precipitation Anomalies (LOF)**
  - Adjust contamination slider
  - Adjust neighbors slider
  - Verify scatter plot shows anomalies in red
  - Check metric cards
  - Expand "View Anomaly Details"
- ✅ Expand "Data Source" at bottom

**Page 7: Mongo Status** (Extra)
- ✅ Check connection status

---

### **Option 2: Test Jupyter Notebook**

#### **Step 1: Open Jupyter**
```bash
cd /home/hishamtariq/aoun_assessment/ind320-portfolio-isma
jupyter notebook notebooks/IND320_Assignment3_Start.ipynb
```

#### **Step 2: Run All Cells**
- Click: **Kernel → Restart & Run All**
- Or: **Cell → Run All**

#### **Step 3: Verify Outputs**

**Expected Outputs:**
1. ✅ Project root and data directory paths displayed
2. ✅ City DataFrame with 5 cities
3. ✅ Bergen 2019 weather data downloaded
4. ✅ Temperature plot with outliers highlighted
5. ✅ Outlier statistics displayed
6. ✅ Precipitation plot with anomalies highlighted
7. ✅ Anomaly statistics displayed
8. ✅ Production data loaded (175,200 records)
9. ✅ STL decomposition plot (4 components)
10. ✅ Spectrogram plot

**Check for Errors:**
- ❌ No `NameError` (df_prod should be defined)
- ❌ No path errors (should find data/production_2021.csv)
- ❌ No import errors (all packages installed)

---

### **Option 3: Quick Validation Tests**

#### **Test 1: Notebook Structure**
```bash
cd /home/hishamtariq/aoun_assessment/ind320-portfolio-isma
python test_notebook.py
```

**Expected Output:**
```
✓ Notebook found
✓ Total cells: 33
✓ Found 9/9 required components
✓ All required components found!
```

#### **Test 2: Component Functionality**
```bash
notebook_env/bin/python test_components.py
```

**Expected Output:**
```
✓ All imports successful
✓ City DataFrame created (5 cities)
✓ API function defined
✓ Production data loaded (175,200 records)
✓ DCT working
✓ LOF working
```

---

## 📋 **Testing Checklist**

### **Jupyter Notebook:**
- [ ] Opens without errors
- [ ] All cells run successfully
- [ ] City DataFrame displays 5 cities
- [ ] Bergen 2019 data downloads
- [ ] Temperature outlier plot shows red points
- [ ] Precipitation anomaly plot shows red points
- [ ] Production data loads (175,200 records)
- [ ] STL plot shows 4 components
- [ ] Spectrogram displays
- [ ] No errors in any cell
- [ ] All plots visible

### **Streamlit App:**
- [ ] App starts without errors
- [ ] All 7 pages accessible
- [ ] Page 3 (Analysis A) has 2 tabs
- [ ] Page 6 (Analysis B) has 2 tabs
- [ ] STL plot displays
- [ ] Spectrogram displays
- [ ] Temperature outlier plot displays
- [ ] Precipitation anomaly plot displays
- [ ] All sliders work
- [ ] All selectors work
- [ ] Metric cards display
- [ ] Expanders work
- [ ] No error messages

---

## 🐛 **Troubleshooting**

### **Issue: Streamlit won't start**
```bash
# Check if streamlit is installed
pip list | grep streamlit

# If not, install
pip install streamlit

# Or use project environment
source notebook_env/bin/activate
streamlit run app.py
```

### **Issue: Jupyter won't open notebook**
```bash
# Install jupyter if needed
pip install jupyter

# Or use project environment
source notebook_env/bin/activate
jupyter notebook
```

### **Issue: Missing packages**
```bash
# Install all requirements
pip install -r requirements.txt

# Or in project environment
notebook_env/bin/pip install -r requirements.txt
```

### **Issue: Data file not found**
```bash
# Check if file exists
ls -la data/production_2021.csv

# If missing, you may need to run Assignment 2 first
# Or the notebook will create empty DataFrame and skip those analyses
```

### **Issue: MongoDB connection fails**
- This is OK for local testing
- The app has fallbacks for missing MongoDB
- Production data can be loaded from CSV

---

## 📊 **What to Look For**

### **Jupyter Notebook Success Indicators:**
✅ "✓ Production data loaded successfully"  
✅ "Running STL Decomposition..."  
✅ "Generating Spectrogram..."  
✅ Plots display without errors  
✅ Statistics show reasonable numbers  

### **Streamlit App Success Indicators:**
✅ All pages load without errors  
✅ Tabs switch smoothly  
✅ Plots are interactive (zoom, pan)  
✅ Sliders update plots in real-time  
✅ Metric cards show numbers  
✅ No red error messages  

---

## 🎯 **Quick Test Commands**

```bash
# Full test sequence
cd /home/hishamtariq/aoun_assessment/ind320-portfolio-isma

# 1. Test notebook structure
python test_notebook.py

# 2. Test components
notebook_env/bin/python test_components.py

# 3. Run Streamlit app
streamlit run app.py

# 4. (In another terminal) Open Jupyter
jupyter notebook notebooks/IND320_Assignment3_Start.ipynb
```

---

## ✅ **Expected Test Results**

### **All Tests Pass:**
```
✓ Notebook validation: PASS
✓ Component tests: PASS
✓ Streamlit app: RUNNING
✓ Jupyter notebook: ALL CELLS RUN
```

### **Ready for Submission When:**
- ✅ All notebook cells run without errors
- ✅ All plots display correctly
- ✅ Streamlit app runs without errors
- ✅ All 7 pages accessible
- ✅ Both new pages use tabs
- ✅ All analyses produce results

---

## 🚀 **Next Steps After Testing**

1. **If everything works:**
   ```bash
   # Push to GitHub
   git push origin assessment_3_new
   
   # Export notebook to HTML
   # In Jupyter: File → Download as → HTML
   ```

2. **If issues found:**
   - Note the error message
   - Check which cell/page fails
   - Share the error for debugging

---

## 📝 **Testing Summary**

**Time Required:** 10-15 minutes  
**Difficulty:** Easy  
**Prerequisites:** Python, Jupyter, Streamlit installed  

**What You're Testing:**
1. Notebook runs end-to-end
2. All 6 analysis functions work
3. Streamlit app displays all pages
4. New pages A and B use tabs
5. All visualizations display

**Success Criteria:**
- No errors in notebook
- No errors in Streamlit
- All plots visible
- All features functional

---

**Ready to test! 🧪**
