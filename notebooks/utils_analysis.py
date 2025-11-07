# notebooks/utils_analysis.py
import pandas as pd
import numpy as np
import plotly.express as px
from statsmodels.tsa.seasonal import STL

# --------------------------------------------------------------------
# Utility: normalize Elhub column names
# --------------------------------------------------------------------
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "StartTime": "startTime",
        "start_time": "startTime",
        "quantity": "quantitykWh",
        "Quantity": "quantitykWh",
        "quantity_kwh": "quantitykWh",
        "QuantityKWh": "quantitykWh",
    }
    df = df.rename(columns={c: rename_map.get(c, c) for c in df.columns})
    return df


# --------------------------------------------------------------------
# Helper: extract series for area & group safely
# --------------------------------------------------------------------
def _series(df: pd.DataFrame, area: str, group: str):
    df = normalize_columns(df)
    required = {"priceArea", "productionGroup", "startTime", "quantitykWh"}
    if not required.issubset(df.columns):
        missing = required - set(df.columns)
        raise KeyError(f"Missing columns in dataframe: {missing}")

    ts = (
        df[(df["priceArea"] == area) & (df["productionGroup"] == group)]
        .sort_values("startTime")[["startTime", "quantitykWh"]]
        .dropna()
    )
    return ts


# --------------------------------------------------------------------
# STL decomposition plot
# --------------------------------------------------------------------
def stl_production_plot(df, area="NO5", group="Hydro",
                        period=24 * 7, seasonal=13, trend=31, robust=True):
    df = normalize_columns(df)
    ts = _series(df, area, group)
    if ts.empty:
        raise ValueError(f"No data for area={area}, group={group}")

    ts = ts.set_index("startTime")
    res = STL(ts["quantitykWh"], period=period, seasonal=seasonal,
              trend=trend, robust=robust).fit()

    decomp = pd.DataFrame({
        "time": ts.index,
        "Observed": res.observed,
        "Trend": res.trend,
        "Seasonal": res.seasonal,
        "Residual": res.resid
    })

    fig = px.line(
        decomp.melt(id_vars="time", var_name="Component", value_name="kWh"),
        x="time", y="kWh", color="Component",
        title=f"STL Decomposition — {area} / {group}"
    )
    fig.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="white"), legend_title="Component",
        hovermode="x unified", margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig
