Project Intermediate Submission

Peter Lu
University of Southern California
DSCI 510: Principles of Programming for Data Science
USD ID: 4353709442

April 14, 2026

---

Getting Started

This project uses a Python virtual environment (.venv) for dependency isolation. You can set it up using either uv (recommended) or standard venv + pip.

---

Option 1: Using uv (Recommended)

1. Install dependencies + create .venv

uv sync

This automatically:
- Creates .venv
- Installs all dependencies from pyproject.toml / lock file

2. Activate environment

source .venv/bin/activate

3. (If needed) install from requirements.txt

uv pip install -r requirements.txt

---

Option 2: Without uv (Standard Python venv)

1. Create virtual environment

python -m venv .venv

2. Activate environment

Mac/Linux:
source .venv/bin/activate

Windows (PowerShell):
.venv\Scripts\activate

3. Install dependencies

pip install -r requirements.txt

---

Running the Program

Run the scraper:

python scraper.py

---

CLI Usage

Scrape a limited number of airports:

python scraper.py --scrape 10

Save output to CSV:

python scraper.py --save my_scraped_data.csv

Save to nested directory:

python scraper.py --save dir1/dir2/my_scraped_data.csv

---

Notes

- Ensure .venv is activated before running any commands
- uv is recommended for faster dependency resolution
- Output format is configurable via CLI flags