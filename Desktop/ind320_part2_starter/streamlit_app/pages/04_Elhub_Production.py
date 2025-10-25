import streamlit as st
import pandas as pd
from pymongo import MongoClient
import plotly.express as px

def app():
    # --- Page Setup ---
    st.set_page_config(page_title="Elhub Production Dashboard", page_icon="⚡", layout="wide")

    st.markdown("""
    <div style="text-align:center; padding-top:0.5rem;">
        <h1 style="color:#F4C430;">⚡ Elhub Production Dashboard</h1>
        <p style="color:gray;">Interactive analysis of Norway's electricity production (MongoDB + Streamlit)</p>
    </div>
    """, unsafe_allow_html=True)

    # --- MongoDB Connection ---
    mongo_uri = "mongodb+srv://ismasohail_user:IsmaMinhas@cluster0.e3wct64.mongodb.net/ind320?retryWrites=true&w=majority&appName=Cluster0"
    try:
        client = MongoClient(mongo_uri)
        db = client["ind320"]
        collection = db["elhub_prod_2021"]
        data = list(collection.find({}, {"_id": 0}))
        df = pd.DataFrame(data)
        if df.empty:
            st.warning("⚠️ No data found in MongoDB collection 'elhub_prod_2021'.")
            return
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return

    # --- Data Preparation ---
    df.columns = [c.strip() for c in df.columns]
    q_col = next((c for c in ["quantitykWh", "quantityKwh", "quantity_kWh", "quantity", "quantityKWh"] if c in df.columns), None)
    if not q_col:
        st.error("❌ Could not find a 'quantity' column in dataset.")
        return

    if "startTime" in df.columns:
        df["startTime"] = pd.to_datetime(df["startTime"], errors="coerce", utc=True)
        df["localTime"] = df["startTime"].dt.tz_convert("Europe/Oslo")
        df["Month"] = df["localTime"].dt.strftime("%b %Y")
        df["Date"] = df["localTime"].dt.date

    # --- Layout ---
    col_left, col_right = st.columns(2)

    # ========================= LEFT COLUMN =========================
    with col_left:
        st.subheader("📍 Select Price Area")
        price_areas = sorted(df["priceArea"].unique().tolist())
        selected_area = st.radio("Choose a Price Area:", price_areas, horizontal=True)
        area_df = df[df["priceArea"] == selected_area]

        # --- PIE CHART SECTION ---
        st.markdown("### 🥧 Production Share")

        view_option = st.radio(
            "Select Pie Chart View:",
            ["Yearly Total", "Selected Month"],
            horizontal=True,
        )

        if view_option == "Yearly Total":
            grouped = area_df.groupby("productionGroup", as_index=False)[q_col].sum()
            pie_title = f"Total Production Share — {selected_area} (2021)"
        else:
            # dynamically filter by month
            if "Month" in df.columns:
                available_months = sorted(df["Month"].unique().tolist())
                selected_month_pie = st.selectbox("📅 Choose Month for Pie Chart", available_months)
                month_df = area_df[area_df["Month"] == selected_month_pie]
                grouped = month_df.groupby("productionGroup", as_index=False)[q_col].sum()
                pie_title = f"Production Share — {selected_month_pie} ({selected_area})"
            else:
                grouped = area_df.groupby("productionGroup", as_index=False)[q_col].sum()
                pie_title = f"Total Production Share — {selected_area}"

        fig_pie = px.pie(
            grouped,
            names="productionGroup",
            values=q_col,
            title=pie_title,
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            title_font=dict(size=18, color="#F4C430"),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ========================= RIGHT COLUMN =========================
    with col_right:
        st.subheader("⚙️ Select Production Groups & Month")

        available_groups = sorted(df["productionGroup"].unique().tolist())
        selected_groups = st.pills(
            "Production Groups:",
            available_groups,
            selection_mode="multi",
            default=available_groups[:2],
        )

        available_months = sorted(df["Month"].unique().tolist())
        selected_month = st.selectbox("📅 Choose Month for Line Chart", available_months)

        filtered = df[
            (df["priceArea"] == selected_area) &
            (df["productionGroup"].isin(selected_groups)) &
            (df["Month"] == selected_month)
        ]

        st.markdown(f"### 📈 Hourly Production — {selected_month} ({selected_area})")
        if filtered.empty:
            st.warning("No data for this selection.")
        else:
            fig_line = px.line(
                filtered,
                x="localTime",
                y=q_col,
                color="productionGroup",
                markers=True,
                title="Hourly Production Trend",
                color_discrete_sequence=px.colors.qualitative.Set3,
            )
            fig_line.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                title_font=dict(size=18, color="#F4C430"),
                xaxis_title="Local Time (Europe/Oslo)",
                yaxis_title="Production (kWh)",
            )
            st.plotly_chart(fig_line, use_container_width=True)

    # ========================= EXPANDER SECTION =========================
    with st.expander("📘 Data Source & Time Handling"):
        st.markdown("""
        **Source:** Simulated Elhub dataset inspired by [api.elhub.no](https://api.elhub.no)  
        **Dataset Description:** Hourly production data across 4 Norwegian price areas.  

        **Time Encoding Notes:**
        - Stored timestamps are UTC.
        - Converted to **Europe/Oslo** timezone to reflect summer/winter transitions.
        - This ensures DST accuracy when analyzing hourly data across months.
        """)

    # --- Footer ---
    st.markdown("""
    <hr>
    <div style="text-align:center; color:gray; font-size:0.9rem;">
        <em>IND320 Portfolio — Part 2 | MongoDB + Streamlit | By Isma Sohail (2025)</em>
    </div>
    """, unsafe_allow_html=True)
