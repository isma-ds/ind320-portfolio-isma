import streamlit as st
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

st.title("Plots")
st.write("Plot any single column or all columns together. Use the month selector to choose a subset.")

CSV_PATH = Path(__file__).parent / "open-meteo-subset.csv"

@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

if not CSV_PATH.exists():
    st.error("CSV not found: `open-meteo-subset.csv`. Please add it to the app folder.")
else:
    df = load_data(CSV_PATH)

    # Try to guess a month index; if no clear month column exists, simulate by chunking every 30 rows
    total_rows = len(df)
    approx_months = max(1, total_rows // 30)
    month_ids = [f"Month {i+1}" for i in range(approx_months)]

    choice = st.selectbox("Choose a column (or All)", ["All"] + list(df.columns))
    month = st.select_slider("Select month", options=month_ids, value=month_ids[0])

    # Calculate row window for the selected month (30-row chunks)
    idx = month_ids.index(month)
    start = idx * 30
    end = min(start + 30, total_rows)
    subset = df.iloc[start:end]

    st.caption(f"Showing rows {start}–{end} ({len(subset)} rows)")

    fig, ax = plt.subplots()
    if choice == "All":
        for c in subset.columns:
            if pd.api.types.is_numeric_dtype(subset[c]):
                ax.plot(subset.index, subset[c], label=c)
        ax.set_title("All Columns")
        ax.set_xlabel("Index")
        ax.set_ylabel("Value")
        ax.legend(loc="best")
    else:
        if pd.api.types.is_numeric_dtype(subset[choice]):
            ax.plot(subset.index, subset[choice], label=choice)
            ax.set_title(choice)
            ax.set_xlabel("Index")
            ax.set_ylabel("Value")
            ax.legend(loc="best")
        else:
            st.warning("Selected column is non-numeric; cannot plot line chart.")
    st.pyplot(fig, clear_figure=True)
