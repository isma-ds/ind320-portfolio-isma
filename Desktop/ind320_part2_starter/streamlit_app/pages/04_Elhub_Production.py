
import os
import pandas as pd
import plotly.express as px
import streamlit as st
from pymongo import MongoClient

st.title("Page 4 — Elhub Production (MongoDB)")

# ---- Mongo Connection ----
uri = st.secrets.get("MONGODB_URI", os.environ.get("MONGODB_URI", ""))
db_name = st.secrets.get("MONGODB_DB", os.environ.get("MONGODB_DB", "ind320"))
coll_name = st.secrets.get("MONGODB_COLLECTION", os.environ.get("MONGODB_COLLECTION", "elhub_production"))

if not uri:
    st.error("Missing MongoDB connection string. Set MONGODB_URI in secrets.toml or env.")
    st.stop()

client = MongoClient(uri)
db = client[db_name]
coll = db[coll_name]

# ---- Load data from MongoDB ----
cursor = coll.find({}, {"_id": 0, "priceArea": 1, "productionGroup": 1, "startTime": 1, "quantityKwh": 1})
df = pd.DataFrame(list(cursor))

if df.empty:
    st.warning("MongoDB collection is empty. Run the Notebook to insert data first.")
    st.stop()

# Ensure dtypes
df["startTime"] = pd.to_datetime(df["startTime"], utc=True)
df["month"] = df["startTime"].dt.month
df["year"] = df["startTime"].dt.year

# ---- UI layout ----
left, right = st.columns(2)

with left:
    price_areas = sorted(df["priceArea"].dropna().unique().tolist())
    selected_area = st.radio("Select price area", options=price_areas, horizontal=True if len(price_areas) <= 5 else False)
    area_df = df[df["priceArea"] == selected_area]
    total_by_group = area_df.groupby("productionGroup", as_index=False)["quantityKwh"].sum()
    fig_pie = px.pie(total_by_group, names="productionGroup", values="quantityKwh", title=f"Total production by group — {selected_area}")
    st.plotly_chart(fig_pie, use_container_width=True)

with right:
    groups = sorted(df["productionGroup"].dropna().unique().tolist())
    try:
        selected_groups = st.pills("Production groups", options=groups, selection_mode="multi", default=groups[:3] if len(groups) >=3 else groups)
    except Exception:
        # older Streamlit fallback: use multiselect
        selected_groups = st.multiselect("Production groups", options=groups, default=groups[:3] if len(groups) >=3 else groups)
    month_map = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}
    months = sorted(df["month"].unique().tolist())
    month_labels = [month_map[m] for m in months]
    selected_month_label = st.selectbox("Month", options=month_labels, index=0)
    inv_map = {v:k for k,v in month_map.items()}
    selected_month = inv_map[selected_month_label]

    f = (df["priceArea"] == selected_area) & (df["month"] == selected_month)
    if selected_groups:
        f &= df["productionGroup"].isin(selected_groups)

    month_df = df.loc[f].copy()
    if month_df.empty:
        st.warning("No data for that combination.")
    else:
        month_df = month_df.sort_values("startTime")
        fig_line = px.line(month_df, x="startTime", y="quantityKwh", color="productionGroup",
                           title=f"Hourly production — {selected_area}, {selected_month_label}")
        st.plotly_chart(fig_line, use_container_width=True)

with st.expander("Data source & notes"):
    st.markdown(
        """
**Source:** Elhub Energy Data API — `PRODUCTION_PER_GROUP_MBA_HOUR` (hourly production by production group and price area).

Data were fetched in the Jupyter Notebook, written to Cassandra/Spark, then exported to MongoDB.
        """
    )
