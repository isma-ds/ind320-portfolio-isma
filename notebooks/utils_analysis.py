import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import STL
from scipy.signal import spectrogram

def _series(df, area, group):
    ts = (df[(df["priceArea"]==area) & (df["productionGroup"]==group)]
          .sort_values("startTime")[["startTime","quantityKwh"]]
          .set_index("startTime")["quantityKwh"]
          .asfreq("H").interpolate(limit_direction="both"))
    return ts

def stl_production_plot(df, area="NO5", group="Hydro",
                        period=24*7, seasonal=13, trend=31, robust=True):
    ts = _series(df, area, group)
    n = len(ts.dropna())
    if n < period*2:
        period = max(5, n//5)
    if trend <= period:
        trend = period + 1
    if trend % 2 == 0:
        trend += 1
    res = STL(ts, period=period, seasonal=seasonal, trend=trend, robust=robust).fit()
    fig = res.plot()
    fig.suptitle(f"STL — {area}/{group}  (period={period}, trend={trend}, seasonal={seasonal})", y=1.03)
    fig.tight_layout()
    return fig

def spectrogram_production_plot(df, area="NO5", group="Hydro",
                                window_len=24*7, overlap=0.5):
    ts = _series(df, area, group)
    f, t, Sxx = spectrogram(ts.values, nperseg=window_len, noverlap=int(window_len*overlap))
    fig, ax = plt.subplots(figsize=(8,4))
    ax.pcolormesh(t, f, 10*np.log10(Sxx+1e-9), shading="gouraud")
    ax.set_title(f"Spectrogram — {area}/{group} (window={window_len}, overlap={overlap})")
    ax.set_xlabel("Window index"); ax.set_ylabel("Frequency (arb.)")
    fig.tight_layout()
    return fig
