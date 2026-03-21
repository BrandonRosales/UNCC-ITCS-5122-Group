# Team 10 — Economic Recovery Trackers

**ITCS 5122 Visual Analytics | UNCC | Spring 2026**

**Role:** Investment Bank Risk Analysts
**Business Problem:** Identify ZIP codes experiencing wealth exodus vs. economic growth to guide lending decisions.
**Data:** IRS Statistics of Income (SOI) ZIP-level tax returns — 5-year window (2018–2022).

---

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app fetches IRS data directly from [irs.gov](https://www.irs.gov/pub/irs-soi/) on first load (~2 minutes for 5 years), then caches to disk (`.data_cache/`) so subsequent runs are instant.

## Project Structure

```
.
├── app.py            # Streamlit entry point, layout, sidebar filters
├── data_loader.py    # IRS data fetching, caching, AGI/IQRI computation
├── phase1.py         # Phase 1 visualizations (AGI growth analysis)
├── phase2.py         # Phase 2 visualizations (IQRI income quality index)
├── utils.py          # Color palettes, constants, IRS URLs
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

---

## Data Sources

- [IRS SOI 2022 ZIP-level data](https://www.irs.gov/pub/irs-soi/22zpallagi.csv)
- [IRS SOI 2021 ZIP-level data](https://www.irs.gov/pub/irs-soi/21zpallagi.csv)
- [IRS SOI 2020 ZIP-level data](https://www.irs.gov/pub/irs-soi/20zpallagi.csv)
- [IRS SOI 2019 ZIP-level data](https://www.irs.gov/pub/irs-soi/19zpallagi.csv)
- [IRS SOI 2018 ZIP-level data](https://www.irs.gov/pub/irs-soi/18zpallagi.csv)

**Key IRS Columns Used:**
| Column | Description |
|---|---|
| `A00100` | Adjusted Gross Income (AGI) |
| `A00200` | Wages & Salaries |
| `A00600` | Dividends |
| `A00900` | Business Income |
| `N1` | Number of Tax Returns |
