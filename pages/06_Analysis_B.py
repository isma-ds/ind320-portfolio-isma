import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor
from scipy.fftpack import dct, idct

st.set_page_config(page_title="Analysis B", page_icon="⚡", layout="wide")
st.title("⚡ Analysis B — SPC & LOF (Open-Meteo 2021)")

df = st.session_state.get("ind320_meteo_df")
city = st.session_state.get("ind320_city", "Bergen")
if df is None:
    st.error("No ERA5 data is cached yet. Open **02_PriceArea** first.")
    st.stop()

df = df.copy()
df["time"] = pd.to_datetime(df["time"], utc=True)

tab1, tab2 = st.tabs(["SPC (temp)", "LOF (precip)"])

def _dct_highpass(x, cutoff=30):
    X = dct(x, type=2, norm="ortho")
    low = X.copy(); low[cutoff:] = 0
    trend = idct(low, type=2, norm="ortho")
    return x - trend, trend

def _mad_std(x):
    med = np.median(x); mad = np.median(np.abs(x-med))
    return 1.4826*mad

with tab1:
    cutoff = st.slider("DCT cutoff", 5, 100, 30, step=5)
    k = st.slider("k·σ (limits)", 1.0, 5.0, 3.0, step=0.5)
    dft = df[["time","temperature_2m"]].dropna().copy()
    x = dft["temperature_2m"].to_numpy(float)
    satv, trend = _dct_highpass(x, cutoff)
    sigma = _mad_std(satv)
    ub, lb = trend + k*sigma, trend - k*sigma
    out = (satv > k*sigma) | (satv < -k*sigma)

    fig, ax = plt.subplots(figsize=(11,4))
    ax.plot(dft["time"], x, lw=1.0, label="Temp")
    ax.plot(dft["time"], ub, lw=1.0, ls="--", label=f"+{k}σ")
    ax.plot(dft["time"], lb, lw=1.0, ls="--", label=f"-{k}σ")
    ax.scatter(dft.loc[out,"time"], dft.loc[out,"temperature_2m"], s=10, label="Outliers")
    ax.set_title(f"{city} — SPC on temperature")
    ax.legend(loc="best"); ax.set_xlabel("UTC"); ax.set_ylabel("°C")
    st.pyplot(fig, use_container_width=True)

    st.json({"points": int(len(dft)), "outliers": int(out.sum()), "pct": round(float(out.mean()*100),2)})

with tab2:
    contamination = st.slider("LOF contamination", 0.001, 0.10, 0.01, step=0.005)
    dfp = df[["time","precipitation"]].dropna().copy()
    X = dfp["precipitation"].to_numpy().reshape(-1,1)
    lof = LocalOutlierFactor(n_neighbors=35, contamination=contamination)
    labels = lof.fit_predict(X)
    dfp["is_outlier"] = (labels==-1)

    fig2, ax2 = plt.subplots(figsize=(11,4))
    ax2.plot(dfp["time"], dfp["precipitation"], lw=1.0, label="Precip")
    ax2.scatter(dfp.loc[dfp.is_outlier,"time"], dfp.loc[dfp.is_outlier,"precipitation"], s=12, label="LOF")
    ax2.set_title(f"{city} — LOF on precipitation")
    ax2.set_xlabel("UTC"); ax2.set_ylabel("mm"); ax2.legend(loc="best")
    st.pyplot(fig2, use_container_width=True)

    st.json({"points": int(len(dfp)), "anomalies": int(dfp.is_outlier.sum()),
             "pct": round(float(dfp.is_outlier.mean()*100),2), "contamination": float(contamination)})
