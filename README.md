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
- Handles missing data and special placeholders
- Reusable and testable class-based architecture
- Saves results to `.csv` (can easily extend to SQLite or other formats)

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
```