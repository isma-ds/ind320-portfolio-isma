
# IND320 — Part 2 Starter (Elhub • Spark/Cassandra • MongoDB • Streamlit)

This kit contains:
- `notebooks/IND320_Part2.ipynb` — step-by-step Notebook per assignment.
- `streamlit_app/` — multi-page app. Page 4 implements MongoDB charts.
- `requirements.txt` — Python dependencies.
- `.streamlit/secrets.example.toml` — copy to `secrets.toml` and fill.

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run the notebook
jupyter notebook notebooks/IND320_Part2.ipynb

# Run the Streamlit app locally
cd streamlit_app
streamlit run Home.py
```

## Branching workflow
Create a temp branch while waiting for review:
```bash
git checkout -b part2-work
git add .
git commit -m "IND320 Part 2 — initial scaffold"
git push -u origin part2-work
```
After peer feedback, merge into `main` via Pull Request.
