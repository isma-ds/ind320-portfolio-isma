import streamlit as st

st.title("About / Log / AI Usage")

st.subheader("Project Info")
st.markdown(
"""
**Course:** IND320  
**Author:** Isma Sohail  
**App:** Multi‑page Streamlit app reading local CSV with caching
"""
)

st.subheader("AI Usage (Brief)")
st.markdown(
"""
I used AI tools to:  
- Draft initial code structure for a Streamlit multi‑page app and Jupyter Notebook.  
- Suggest Pandas/Matplotlib snippets and caching patterns in Streamlit.  
- Improve clarity of headings and docstrings.  
All generated code/comments were reviewed and adapted by me.
"""
)

st.subheader("Work Log (300–500 words)")
st.markdown(
"""
During this iteration, I set up a GitHub repository and a minimal Streamlit app, focusing on a clean structure and clear navigation. 
I ensured reproducibility by adding a `requirements.txt` and comments explaining each block. 
Locally, I verified that the app reads a CSV file from disk, caches the data for speed, and supports multiple pages. 
The sidebar routes the user to the Data Table and Plots pages, which demonstrate essential functionality for the course requirements.

In the Jupyter Notebook, I loaded the CSV using Pandas, printed a concise preview, and produced plots for each column separately and all columns together. 
To handle columns on different scales, I deliberately showed per‑column plots as well as a combined view, noting the interpretability trade‑offs. 
I kept the headings explicit so that the notebook doubles as documentation while I iterate on the project.

I used AI as a supportive tool for boilerplate generation and code organization. 
Specifically, I asked for help with a robust multipage layout and a safe fallback when the CSV is missing. 
I also leveraged suggestions for using `st.column_config.LineChartColumn` to give a compact, row‑wise visualization of the first month in the table view. 
Where AI output did not fit my exact dataset layout, I refactored the code and added defensive checks. 
I found that draft generation significantly reduced time spent on routine tasks, allowing me to focus on understanding the data and refining the UX.

Next, I plan to connect the app to a public dataset or export curated subsets to CSV to satisfy the later database requirements. 
I will extend the plot page with richer labeling, tooltips, and optional rescaling. 
Finally, I intend to document deployment steps in the README and add a short screencast to demonstrate core features.
"""
)
