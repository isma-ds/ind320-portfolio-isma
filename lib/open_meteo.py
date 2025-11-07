# lib/open_meteo.py
# ---------------------------------
# ERA5 download helpers for Open-Meteo + a cache helper for Streamlit pages.

from __future__ import annotations
import requests
import pandas as pd
import numpy as np

# ---- Default hourly variables we use across the assignment ----
HOURLY_VARS = ["temperature_2m", "precipitation", "relative_humidity_2m", "wind_speed_10m"]

def fetch_era5(lat: float, lon: float, year: int, hourly_vars: list[str] = HOURLY_VARS) -> pd.DataFrame:
    """
    Download ERA5 hourly data (UTC) for one location/year with selected variables.
    Uses Open-Meteo archive ERA5 endpoint.
    """
    url = "https://archive-api.open-meteo.com/v1/era5"
    params = {
        "latitude":  lat,
        "longitude": lon,
        "start_date": f"{year}-01-01",
        "end_date":   f"{year}-12-31",
        "hourly": ",".join(hourly_vars),
        "timezone": "UTC",
    }
    r = requests.get(url, params=params, timeout=90)
    r.raise_for_status()
    j = r.json()

    if "hourly" not in j or "time" not in j["hourly"]:
        raise RuntimeError("Open-Meteo ERA5: response missing 'hourly'/'time'.")

    df = pd.DataFrame({"time": pd.to_datetime(j["hourly"]["time"], utc=True)})
    for v in hourly_vars:
        df[v] = j["hourly"].get(v, [np.nan] * len(df))
    return df


# ------------ Streamlit cache helper ------------
# Lets Analysis pages work even after a cold start in the cloud.
def get_or_fetch_era5(st, area_code: str, lat: float, lon: float, year: int = 2021,
                      hourly_vars: list[str] = HOURLY_VARS) -> pd.DataFrame:
    """
    Ensure ERA5 df exists in st.session_state. Returns a DataFrame guaranteed to exist.
    Cache key is (area_code, year, hourly_vars).
    """
    key = f"era5_{area_code}_{year}_{'+'.join(hourly_vars)}"
    if "era5_cache" not in st.session_state:
        st.session_state["era5_cache"] = {}

    cache = st.session_state["era5_cache"]
    if key in cache and isinstance(cache[key], pd.DataFrame) and not cache[key].empty:
        return cache[key]

    df = fetch_era5(lat=lat, lon=lon, year=year, hourly_vars=hourly_vars)
    cache[key] = df
    return df
