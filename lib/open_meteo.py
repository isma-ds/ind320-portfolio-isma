import pandas as pd, requests

DEFAULT_VARS = ["temperature_2m","precipitation","relative_humidity_2m","wind_speed_10m"]

def fetch_era5(lat, lon, year, vars=DEFAULT_VARS):
    url = "https://archive-api.open-meteo.com/v1/era5"
    p = {
        "latitude": lat, "longitude": lon,
        "start_date": f"{year}-01-01", "end_date": f"{year}-12-31",
        "hourly": ",".join(vars), "timezone": "UTC",
    }
    r = requests.get(url, params=p, timeout=60)
    r.raise_for_status()
    j = r.json()
    df = pd.DataFrame({"time": pd.to_datetime(j["hourly"]["time"], utc=True)})
    for v in vars:
        df[v] = j["hourly"].get(v, [None]*len(df))
    return df
