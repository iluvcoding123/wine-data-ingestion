# Joseph Perrier Wine Data Ingestion

This project was completed as part of a technical assignment for Onki.

## Overview

This tool ingests winery-level and product-level data from the English Joseph Perrier website and stores it in a structured SQLite database.

It captures:
- winery content from core brand pages such as history, family spirit, vineyard, cellar, commitments, and winemaking
- product content from Joseph Perrier cuvée pages
- media records linked to either the winery or individual products

## Stack

- Python
- Requests
- BeautifulSoup
- SQLite

## Database schema

The database contains three main tables:
- `wineries`
- `products`
- `media`

`media` supports both winery-level and product-level assets.

## Project structure

```text
src/
  config.py
  db.py
  scraper.py
  parser.py
  ingest.py

data/
  joseph_perrier.db
```

## How it works

The pipeline:
1. creates the database schema
2. ingests winery pages and updates the single winery record
3. ingests seeded product pages and stores structured product attributes
4. stores media records for both winery and product entities

## Run

From the project root:

```bash
python -m src.ingest
```

## Notes

- Product and winery URL discovery was partially seeded due to site routing behavior under non-browser requests.
- Some fields are page-dependent and may be null when a page does not expose that attribute in a consistent structure.
- The resulting database can be inspected with DB Browser for SQLite.