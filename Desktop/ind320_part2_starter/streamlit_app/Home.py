import streamlit as st
import importlib
import os

# --- Page Config ---
st.set_page_config(page_title="IND320 Portfolio — Part 2", page_icon="📊", layout="wide")

# --- Hide Default Streamlit Page List ---
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.markdown("## 📊 Navigation")

pages = {
    "🏠 Home": "Home",
    "📈 Page 2": "02_Page2",
    "📊 Page 3": "03_Page3",
    "⚡ Elhub Production": "04_Elhub_Production",
    "🧩 Extra": "05_Extra"
}

choice = st.sidebar.selectbox("Choose a page", list(pages.keys()))

# --- Dynamic Page Import ---
if choice == "🏠 Home":
    st.title("IND320 Portfolio — Part 2 (Elhub • Cassandra • MongoDB)")
    st.markdown(
        """
        Welcome to your **IND320 Project Dashboard**  
        Use the sidebar to explore each section:
        - Page 2 and Page 3 contain visual analytics  
        - Elhub Production integrates Cassandra + Spark  
        - Extra section includes experimental modules  
        """
    )
    st.info("Select a page from the sidebar dropdown to begin.")
else:
    module_name = pages[choice]
    try:
        mod = importlib.import_module(f"pages.{module_name}")
        if hasattr(mod, "app"):
            mod.app()  # if the file defines app()
        else:
            st.warning("⚠️ This page doesn’t have an app() function yet.")
    except Exception as e:
        st.error(f"❌ Error loading {module_name}: {e}")
