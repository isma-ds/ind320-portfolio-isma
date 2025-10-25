
import streamlit as st

st.set_page_config(page_title="IND320 Portfolio — Part 2", page_icon="⚡", layout="wide")
st.title("IND320 Portfolio — Part 2 (Elhub • Cassandra • MongoDB)")
st.markdown(
    """
**This is your Part 2 starter app.**
- Page 4 implements the required MongoDB-powered charts (pie + line with filters).
- Secrets are read from `.streamlit/secrets.toml` when deployed at streamlit.app.
    """
)
st.info("Use the left sidebar to navigate to other pages.")
