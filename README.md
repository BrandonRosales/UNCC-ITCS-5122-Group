# Team 10 — Economic Recovery Trackers

## Project Description

Streamlit app for investment bank risk analysts to identify ZIP codes experiencing wealth exodus vs. economic growth. Analyzes 5 years of IRS Statistics of Income (SOI) ZIP-level tax data (27,000+ ZIPs, 2018–2022) across three phases: AGI CAGR growth analysis (Phase 1), Income Quality & Resilience Index (Phase 2), and an AI-powered lending risk memo generator using Google Gemini (Phase 3).

**ITCS 5122 Visual Analytics | UNCC | Spring 2026 | Team 10**

## App Deployment URL

[Add Streamlit Cloud URL after deployment]

## Local Setup Instructions

```bash
git clone https://github.com/brandonrosales/UNCC-ITCS-5122-Group.git
cd UNCC-ITCS-5122-Group
uv sync
uv run streamlit run app.py
```

To enable the AI Risk Analyst tab, provide `GOOGLE_API_KEY` before running the app. The app now loads a local `.env` file automatically, and you can also set the variable in your shell or copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in your key.

The app fetches IRS data directly from [irs.gov](https://www.irs.gov/pub/irs-soi/) on first load (~2 minutes for 5 years), then caches to disk (`.data_cache/`) so subsequent runs are instant.

---

## Project Structure

```
.
├── app.py            # Streamlit entry point, layout, sidebar filters
├── data_loader.py    # IRS data fetching, caching, AGI/IQRI computation
├── phase1.py         # Phase 1 visualizations (AGI growth analysis)
├── phase2.py         # Phase 2 visualizations (IQRI income quality index)
├── phase3.py         # Phase 3 AI Risk Analyst (Gemini-powered lending memos)
├── utils.py          # Color palettes, constants, IRS URLs
├── requirements.txt  # Python dependencies (Streamlit Cloud)
├── pyproject.toml    # uv project file
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
