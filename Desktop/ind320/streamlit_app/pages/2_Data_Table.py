import streamlit as st
import pandas as pd
from pathlib import Path

st.title("Data Table")
st.write("This page shows the imported data and a small sparkline per column for the **first month**.")

CSV_PATH = Path(__file__).parent / "open-meteo-subset.csv"

@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

if CSV_PATH.exists():
    df = load_data(CSV_PATH)

    # Assume there's a datetime or month column; try to infer the first 30/31 rows if monthly data is row-wise.
    # If the file has a 'time' column, feel free to filter by month explicitly later.
    first_month_df = df.head(31)

    # Build a row-wise table: one row per column with a small line chart sparkline of the first month
    # Using Streamlit's Column Config LineChartColumn
    try:
        # Convert the first month into a dict of lists per column (excluding non-numeric columns)
        numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        small = {}
        for c in numeric_cols:
            small[c] = first_month_df[c].tolist()

        # Prepare a dataframe with one row per column
        table = pd.DataFrame({
            "column": numeric_cols,
            "first_month": [small[c] for c in numeric_cols],
        })

        st.dataframe(
            table,
            column_config={
                "first_month": st.column_config.LineChartColumn(
                    "First Month Trend", width="medium", y_min=None, y_max=None
                )
            },
            hide_index=True,
            use_container_width=True,
        )
    except Exception as e:
        st.warning(f"Could not render LineChartColumn view. Showing raw data instead.\nError: {e}")
        st.dataframe(df.head(), use_container_width=True)

else:
    st.error("CSV not found: `open-meteo-subset.csv`. Please add it to the app folder.")
    uploaded = st.file_uploader("Or upload it here to preview", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        st.dataframe(df.head(), use_container_width=True)
