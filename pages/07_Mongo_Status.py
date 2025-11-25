import streamlit as st
import pandas as pd

st.set_page_config(page_title="MongoDB", page_icon="🗄️", layout="wide")
st.title("🗄️ A2 — MongoDB connection status")

ok = False
try:
    from pymongo import MongoClient
    uri = st.secrets.get("MONGO_URI", None)
    if uri:
        client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        ok = True
except Exception as e:
    st.warning(f"Mongo not connected: {e}")

if ok:
    st.success("MongoDB connected via secrets ✅")
else:
    st.info("Add `MONGO_URI` to **st.secrets** for cloud deploy; local fallback uses CSV files in `/data`.")
