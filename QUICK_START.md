# 🚀 Quick Start Guide - Assignment 3

## Open the Notebook

```bash
cd /home/hishamtariq/aoun_assessment/ind320-portfolio-isma
source notebook_env/bin/activate
jupyter notebook notebooks/IND320_Assignment3_Start.ipynb
```

## What's Inside

### 6 Main Analysis Functions

1. **`download_weather(lat, lon, year)`**
   - Downloads weather data from Open-Meteo API
   - Example: `download_weather(60.39, 5.32, 2019)` for Bergen

2. **`plot_temp_outliers(df, cutoff_freq=0.01, num_std=3)`**
   - Detects temperature outliers using DCT + SPC
   - Returns DataFrame of outliers

3. **`plot_precip_anomalies(df, contamination=0.01)`**
   - Detects precipitation anomalies using LOF
   - Returns DataFrame of anomalies

4. **`plot_stl(price_area, prod_group, period=24, seasonal=7, trend=None, robust=True)`**
   - STL decomposition of production data
   - Example: `plot_stl('NO5', 'Hydro')`

5. **`plot_spectrogram(price_area, prod_group, nperseg=256, noverlap=128)`**
   - Frequency-time analysis
   - Example: `plot_spectrogram('NO5', 'Hydro')`

## Before Submission

- [ ] Run ALL cells in order
- [ ] Update GitHub URL
- [ ] Update Streamlit URL
- [ ] Export to HTML: File → Download as → HTML
- [ ] Verify all plots are visible
- [ ] Check word count in log section (~300-500 words)

## File Locations

- **Notebook**: `notebooks/IND320_Assignment3_Start.ipynb`
- **Data**: `data/production_2021.csv`
- **Requirements**: `requirements.txt`
- **Documentation**: `ASSIGNMENT3_COMPLETE.md`

## Quick Test

```bash
python test_notebook.py
```

Should show: ✓ All required components found!

---

**You're all set! 🎉**
