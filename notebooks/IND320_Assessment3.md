# IND320 Assessment 3 - Implementation Guide

## Overview
This document outlines the implementation of Assessment 3 tasks in the `IND320_Assignment3_Start.ipynb` notebook.

## Tasks Completed

### 1. City Coordinates DataFrame
- Created a DataFrame mapping Norwegian cities to electricity price areas
- Includes: Oslo (NO1), Kristiansand (NO2), Trondheim (NO3), Tromsø (NO4), Bergen (NO5)
- Each city has latitude and longitude coordinates for API calls

### 2. Open-Meteo API Integration
- **Function**: `download_weather(lat, lon, year)`
- Downloads historical weather data using the ERA5 reanalysis model
- Parameters match those from Assessment 1 (temperature, precipitation, humidity, wind speed)
- **Test Case**: Bergen 2019 data downloaded

### 3. Temperature Outlier Detection (DCT + SPC)
- **Function**: `plot_temp_outliers(df, cutoff_freq=0.01, num_std=3)`
- Uses Direct Cosine Transform (DCT) for high-pass filtering
- Creates Seasonally Adjusted Temperature Variations (SATV)
- Applies robust statistics (median + MAD) for Statistical Process Control
- Identifies and highlights outliers in red
- Configurable frequency cutoff and standard deviation threshold

### 4. Precipitation Anomaly Detection (LOF)
- **Function**: `plot_precip_anomalies(df, contamination=0.01)`
- Uses Local Outlier Factor (LOF) algorithm
- Default contamination rate: 1%
- Identifies and highlights anomalies in precipitation data

### 5. STL Decomposition
- **Function**: `plot_stl(price_area, prod_group, period=24, seasonal=7, trend=None, robust=True)`
- Performs Seasonal-Trend decomposition using LOESS
- Works on Elhub production data from Assessment 2
- Configurable parameters for period, seasonal smoother, trend smoother
- Displays: Observed, Trend, Seasonal, and Residual components

### 6. Spectrogram Analysis
- **Function**: `plot_spectrogram(price_area, prod_group, nperseg=256, noverlap=128)`
- Creates frequency-time analysis of production data
- Uses scipy.signal.spectrogram
- Log scale for better visualization
- Configurable window length and overlap

## Data Sources
1. **Open-Meteo API**: Historical weather data (ERA5 model)
2. **Elhub Production Data**: From Assessment 2 (`data/production_2021.csv`)

## Dependencies
All required packages are listed in `requirements.txt`:
- scipy (for DCT, spectrogram)
- statsmodels (for STL decomposition)
- scikit-learn (for LOF)
- seaborn (for enhanced plotting)
- matplotlib, pandas, numpy, requests

## Running the Notebook
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Open `IND320_Assignment3_Start.ipynb` in Jupyter
3. Run cells sequentially from top to bottom
4. All functions include test cases with default parameters

## Notes
- All time data uses UTC timezone
- Production data should be available from Assessment 2
- Functions are designed to be reusable with different parameters
- Plots are configured for clarity with appropriate labels and legends

## Next Steps for Streamlit Integration
- Page reordering (1, 4, New A, 2, 3, New B, 5)
- New Page A: STL and Spectrogram tabs
- New Page B: Outlier/SPC and Anomaly/LOF tabs
- Replace CSV weather import with Open-Meteo API
- Link to price area selector for dynamic data loading
