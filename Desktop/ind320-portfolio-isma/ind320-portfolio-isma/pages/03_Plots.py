import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(page_title="Plots", page_icon="📈", layout="wide")

# --- Styling ---
st.markdown(
    """
<style>
.section {
    background-color: white;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.footer {
    text-align: center;
    font-size: 13px;
    color: #777;
    margin-top: 2rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# --- Sidebar Navigation ---
st.sidebar.title("📂 Navigation")
st.sidebar.page_link("app.py", label="🏠 Home")
st.sidebar.page_link("pages/02_Data_Table.py", label="📊 Data Table")
st.sidebar.page_link("pages/03_Plots.py", label="📈 Plots")
st.sidebar.page_link("pages/04_About.py", label="ℹ️ About")

st.title("📈 Data Visualizations")


@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        df["year_month"] = df["time"].dt.to_period("M").astype(str)
    return df


csv_path = Path("data/open-meteo-subset.csv")
if not csv_path.exists():
    st.error("❌ CSV file not found.")
    st.stop()

df = load_data(csv_path)

months = (
    sorted(df["year_month"].dropna().unique()) if "year_month" in df.columns else []
)
month = st.select_slider(
    "Select Month", options=months, value=months[0] if months else None
)
col_choice = st.selectbox(
    "Choose variable(s)",
    options=["All columns"]
    + [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])],
)

st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("📊 Monthly Plot")

sub = df[df["year_month"] == month] if "year_month" in df.columns else df.head(720)
fig, ax = plt.subplots()
ax.grid(True, linestyle="--", alpha=0.5)

if col_choice == "All columns":
    for c in [c for c in sub.columns if pd.api.types.is_numeric_dtype(sub[c])]:
        ax.plot(sub["time"], sub[c], label=c)
    ax.set_title(f"All Variables ({month})", fontsize=13)
else:
    ax.plot(sub["time"], sub[col_choice], label=col_choice, linewidth=2)
    ax.set_title(f"{col_choice} – {month}", fontsize=13)

ax.set_xlabel("Time")
ax.set_ylabel("Value")
ax.legend(frameon=False)
st.pyplot(fig)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    "<div class='footer'>© 2025 Isma Sohail | IND320 Portfolio</div>",
    unsafe_allow_html=True,
)
