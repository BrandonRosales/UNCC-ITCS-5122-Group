import os
import time
import pandas as pd
import numpy as np
import requests
import streamlit as st
from utils import IRS_URLS, LOAD_COLS, ANALYSIS_YEARS, BASELINE_YEAR, LATEST_YEAR

CACHE_DIR = os.path.join(os.path.dirname(__file__), ".data_cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def _download_with_retry(url: str, dest: str, max_retries: int = 3) -> None:
    """Download a file with retry logic and write to disk."""
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, timeout=120, stream=True)
            resp.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in resp.iter_content(chunk_size=1024 * 256):
                    f.write(chunk)
            return
        except (requests.RequestException, ConnectionError) as e:
            if attempt < max_retries - 1:
                time.sleep(3 * (attempt + 1))  # back off
            else:
                raise RuntimeError(f"Failed to download {url} after {max_retries} attempts: {e}")


@st.cache_data(ttl=86400 * 30, show_spinner=False)  # cache 30 days in Streamlit too
def load_raw(year: int) -> pd.DataFrame:
    """Load a single year, downloading to local disk cache if needed."""
    cache_file = os.path.join(CACHE_DIR, f"{year}_zpallagi.csv")

    if not os.path.exists(cache_file):
        _download_with_retry(IRS_URLS[year], cache_file)

    df = pd.read_csv(
        cache_file,
        usecols=LOAD_COLS,
        dtype={"zipcode": str, "STATE": str},
    )
    return df


@st.cache_data(show_spinner=False)
def build_zip_summary(year: int) -> pd.DataFrame:
    """Aggregate income stub rows into one row per ZIP per state."""
    df = load_raw(year)
    df = df[~df["zipcode"].isin(["0", "00000", "99999"])]
    agg = (
        df.groupby(["zipcode", "STATE"])[
            ["N1", "A00100", "A00200", "A00600", "A00900"]
        ]
        .sum()
        .reset_index()
    )
    agg["year"] = year
    return agg


def build_comparison(_progress_callback=None) -> pd.DataFrame:
    """
    Load all years in ANALYSIS_YEARS, merge, and compute:
      - 5-year CAGR for AGI
      - Year-over-year AGI for trend analysis
      - IQRI from the latest year
    Returns: (merged_df, trend_df)
    """
    summaries = {}
    for i, year in enumerate(ANALYSIS_YEARS):
        summaries[year] = build_zip_summary(year)
        if _progress_callback:
            _progress_callback((i + 1) / len(ANALYSIS_YEARS))

    # ------------------------------------------------------------------
    # Wide-format comparison (baseline vs latest)
    # ------------------------------------------------------------------
    base = summaries[BASELINE_YEAR].rename(
        columns={c: f"{c}_{BASELINE_YEAR}" for c in ["N1", "A00100", "A00200", "A00600", "A00900"]}
    ).drop(columns=["year"])

    latest = summaries[LATEST_YEAR].rename(
        columns={c: f"{c}_{LATEST_YEAR}" for c in ["N1", "A00100", "A00200", "A00600", "A00900"]}
    ).drop(columns=["year"])

    merged = latest.merge(base, on=["zipcode", "STATE"], how="inner")

    # ------------------------------------------------------------------
    # Phase 1: AGI CAGR over 5-year window
    # ------------------------------------------------------------------
    n_years = LATEST_YEAR - BASELINE_YEAR
    agi_start = merged[f"A00100_{BASELINE_YEAR}"].replace(0, np.nan)
    agi_end = merged[f"A00100_{LATEST_YEAR}"]

    ratio = agi_end / agi_start
    valid_ratio = ratio.where(ratio > 0, np.nan)
    merged["agi_cagr"] = (valid_ratio ** (1 / n_years) - 1) * 100
    merged["agi_total_growth_pct"] = ((agi_end - agi_start) / agi_start) * 100

    merged["status"] = merged["agi_cagr"].apply(
        lambda x: "Booming" if x > 4 else ("Shrinking" if x < 0 else "Stable")
        if pd.notna(x) else "Unknown"
    )

    # ------------------------------------------------------------------
    # Phase 2: IQRI from the latest year
    # ------------------------------------------------------------------
    wages = merged[f"A00200_{LATEST_YEAR}"].replace(0, np.nan)
    merged["iqri"] = (merged[f"A00900_{LATEST_YEAR}"] + merged[f"A00600_{LATEST_YEAR}"]) / wages
    merged["iqri_tier"] = pd.cut(
        merged["iqri"],
        bins=[0, 0.05, 0.15, 0.30, float("inf")],
        labels=["Wage-Dependent", "Mixed", "Entrepreneurial", "Investment-Led"],
    )

    # ------------------------------------------------------------------
    # Long-format trend data for year-over-year charts
    # ------------------------------------------------------------------
    trend_frames = []
    for year in ANALYSIS_YEARS:
        s = summaries[year].copy()
        s = s.rename(columns={
            "N1": "returns", "A00100": "agi", "A00200": "wages",
            "A00600": "dividends", "A00900": "business_inc",
        })
        s["year"] = year
        trend_frames.append(s)

    trend_df = pd.concat(trend_frames, ignore_index=True)

    return merged, trend_df
