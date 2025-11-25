ASSIGNMENT 3 — DROP-IN FILES

Put these wherever you like (Desktop ok), then copy into your project:

- IND320_Assignment3.ipynb           → notebooks/
- pages/02_PriceArea.py              → pages/
- pages/03_Analysis_A.py             → pages/
- pages/06_Analysis_B.py             → pages/
- lib/open_meteo.py                  → lib/
- requirements_a3.txt                → (project root)

NEW STREAMLIT ORDER (filenames so Streamlit sorts):
1) 01_Home.py               (your existing page 1)
2) 02_PriceArea.py          (this comes before your old page 2)
3) 03_Analysis_A.py         (NEW A)
4) 04_Data_Table.py         (rename your old page 2 file)
5) 05_Spark_Cassandra.py    (rename your old page 3 file)
6) 06_Analysis_B.py         (NEW B)
7) 07_WhateverWas5.py       (rename your old page 5 file)

Run:
pip3 install -r requirements_a3.txt
streamlit run app.py

Notebook:
Open IND320_Assignment3.ipynb and Run All.
