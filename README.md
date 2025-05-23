# Webscraper Challenge

## Overview
A data scraping and analysis project for structured HTML pages. The pipeline extracts, transforms, and analyzes key web metrics, storing the output in CSV, SQLite, and plot images.

## Features
- Extracts 10+ key datapoints from HTML reports:
  - Global rank
  - Visits, bounce rate, duration, etc.
  - Line/bar chart data (SVG)
  - Top countries and demographics
- Normalizes values (e.g. "9.1M" → 9100000, "00:03:16" → 196 sec)
-  Tracks missing data:
  - Status column: complete, partial, or failed 
  - List of missing fields for quick inspection
- Reusable and testable class-based architecture
-  Modular ETL structure with clean interfaces:
  - Extract → Transform → Load (CSV/SQLite)
  - Controlled via main.py
- Saves results to `.csv` and `.sqlite`
- Auto-generates visual insights:
  - MoM growth (Visits & Rank)
  - Relative growth score by site 
- Fully testable components & error logging

## Deliverables
- Cleaned CSV
- SQLite DB
- PNG graphs

## Structure
```
├── main.py                         # Orchestrator: extract + transform + load menu
├── etl/
│   ├── extract_and_transform.py    # ET logic → returns pandas DataFrame
│   └── load_to_db.py               # Loads DF into SQLite (future extensible to other DBs)
│
├── data/
│   ├── raw_html/                   # Input HTML files
│   ├── logs/                       # Register errors from all extractions
│   └── output/                     # Processed CSV output
|       ├── csv/                    # Processed CSV output
|       └── sqlite/                 # SQLite DBs
│
├── scraper/
│   └── page_parser.py              # HTML parser class with all extractors
│
├── utils/
│   ├── normalizer.py               # Normalization helpers for formats (%, time, numbers)
|   └── error_logger.py             # Logs errors and flags
|
├── responses.md
```

## How to Run
1. Place raw .html files inside data/raw_html/
2. pip install -r requirements.txt
3. From terminal `python main.py`