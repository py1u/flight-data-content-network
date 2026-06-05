# Predicting Weather-Driven Anomalies in US Aviation Networks

**Author:** Peter Lu  
**University:** University of Southern California  
**Date:** May 10, 2026  

---

## How to Install the Requirements

This project uses a **Python virtual environment (.venv)** for dependency isolation. You can set it up using either **uv (recommended)** or standard `venv + pip`.

### Option 1: Using `uv` (Recommended)
1. **Install dependencies and create `.venv`:**
   ```bash
   uv sync
   ```
2. **Activate the environment:**
   ```bash
   source .venv/bin/activate
   ```
3. **Install from requirements.txt (if necessary):**
   ```bash
   uv pip install -r requirements.txt
   ```

### Option 2: Standard Python `venv`
1. **Create virtual environment:**
   ```bash
   python -m venv .venv
   ```
2. **Activate the environment:**
   - Mac/Linux: `source .venv/bin/activate`
   - Windows: `.venv\Scripts\activate`
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## How to Run Your Code

To run the full pipeline, which includes getting data, cleaning data, and analyzing it:
```bash
python src/main.py
```
This script acts as the main wrapper, executing modules sequentially from `src/`.

---

## How to Get the Data

The raw datasets are pulled directly from APIs and other sources. To download and store this data into the `data/raw/` directory, run:
```bash
python src/get_data.py
```
*(Note: This is automatically called if you run `src/main.py`.)*

Alternatively, to run the legacy web scraper for specific airport records, use:
```bash
python scraper.py --save data/raw/my_scraped_data.csv
```

---

## How to Clean Data

Once data is extracted, you can process and structure it to be analyzed. Run:
```bash
python src/clean_data.py
```
This will take data from `data/raw/` and output structured files (like CSV/JSON/Parquet) into `data/processed/`.

---

## How to Run Analysis Code

Data integration and advanced analysis can be done using the integration and analysis scripts:
1. To merge and integrate various data sources into a cohesive structured format:
   ```bash
   python src/integrate_data.py
   ```
2. To compute statistics and analyze the processed data:
   ```bash
   python src/analyze_visualize.py
   ```

---

## How to Produce the Visualizations

Visualizations are generated as part of the analysis process. Running the `analyze_visualize.py` script will automatically create the necessary plots and figures:
```bash
python src/analyze_visualize.py
```
The resulting visual assets and final reports can be found in the `results/` folder, which also holds Jupyter Notebooks used for interactive visualization exploration.
