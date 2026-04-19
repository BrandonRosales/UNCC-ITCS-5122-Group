import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="IRS ZIP Risk Analysis — Team 10",
    page_icon="\U0001f3e6",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme-aware CSS (works in both light and dark mode) ──────────────
st.markdown(
    """
    <style>
    /* Sidebar branded dark navy — always */
    [data-testid="stSidebar"] { background-color: #0A2342; }
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown li,
    [data-testid="stSidebar"] .stMarkdown a,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #E0E0E0 !important; }

    /* Metric values — inherit from theme so they stay visible */
    [data-testid="stMetricValue"] { font-size: 1.6rem; font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)

from data_loader import build_comparison
from phase1 import render_phase1
from phase2 import render_phase2
from phase3 import render_ai_analyst
from utils import BASELINE_YEAR, LATEST_YEAR, ANALYSIS_YEARS

# ── Header ───────────────────────────────────────────────────────────
st.title("\U0001f3e6 Economic Recovery Tracker")
st.markdown(
    f"**Team 10 · Investment Bank Risk Analysis** · "
    f"IRS Statistics of Income ZIP-level data ({BASELINE_YEAR}–{LATEST_YEAR}, "
    f"{len(ANALYSIS_YEARS)}-year window)"
)

st.info(
    "**Client:** Investment bank lending team  \n"
    "**Business Problem:** Lending in economically shrinking ZIP codes exposes the bank to elevated "
    "default risk as local wealth erodes. We need to know *where* wealth is fleeing before we lend.  \n"
    "**Solution:** 5 years of IRS ZIP-level tax data (27,000+ ZIPs) analyzed to identify wealth exodus "
    "vs. booming areas — with AI-generated risk memos for individual ZIP decisions.  \n"
    "**Phase 1** — AGI CAGR: which ZIPs are growing or shrinking?  "
    "**Phase 2** — IQRI: how resilient is each ZIP's income?  "
    "**Phase 3** — AI Risk Analyst: instant lending brief for any ZIP."
)

# ── Load Data with visible progress ─────────────────────────────────
if "df" not in st.session_state or "trend_df" not in st.session_state:
    progress_bar = st.progress(0, text="Downloading IRS data (first run may take ~2 minutes)...")

    def update_progress(pct: float):
        progress_bar.progress(
            pct, text=f"Loading year {int(pct * len(ANALYSIS_YEARS))}/{len(ANALYSIS_YEARS)}..."
        )

    try:
        st.session_state["df"], st.session_state["trend_df"] = build_comparison(
            _progress_callback=update_progress
        )
    except Exception as e:
        progress_bar.empty()
        st.error(f"Failed to load IRS data: {e}")
        st.info("The IRS servers may be slow or unreachable. Please try refreshing the page.")
        st.stop()

    progress_bar.empty()

df = st.session_state["df"]
trend_df = st.session_state["trend_df"]

ALL_STATES = sorted(df["STATE"].dropna().unique())

# ── Sidebar Filters ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Filters")

    selected_states = st.multiselect(
        "State(s)",
        options=ALL_STATES,
        default=[],
        placeholder="All states (none selected)",
        help="Select one or more states. If none are selected, all states are included.",
    )

    min_returns = st.slider(
        f"Min. Returns (N1, {LATEST_YEAR})",
        min_value=0,
        max_value=60000,
        value=2000,
        step=100,
        help="Exclude low-population ZIPs to reduce noise.",
    )

    top_n = st.slider(
        "Top N ZIP codes to display",
        min_value=10,
        max_value=100,
        value=25,
    )

    st.divider()
    st.markdown("### Data Sources")
    source_links = "\n".join(
        f"- [IRS SOI {year}](https://www.irs.gov/pub/irs-soi/{str(year)[2:]}zpallagi.csv)"
        for year in sorted(ANALYSIS_YEARS, reverse=True)
    )
    st.markdown(
        f"{source_links}\n"
        f"- Years loaded: **{', '.join(str(y) for y in ANALYSIS_YEARS)}**"
    )
    st.markdown(
        "**Key Columns**\n"
        "- `A00100` — Adjusted Gross Income\n"
        "- `A00200` — Wages & Salaries\n"
        "- `A00600` — Dividends\n"
        "- `A00900` — Business Income\n"
        "- `N1` — Number of Returns"
    )

# ── Apply Filters ────────────────────────────────────────────────────
n1_col = f"N1_{LATEST_YEAR}"
filtered = df[
    (df["STATE"].isin(selected_states if selected_states else ALL_STATES)) &
    (df[n1_col] >= min_returns)
].copy()

# Filter trend data to match
if selected_states:
    trend_filtered = trend_df[trend_df["STATE"].isin(selected_states)].copy()
else:
    trend_filtered = trend_df.copy()

if filtered.empty:
    st.warning("No ZIP codes match the current filters. Please adjust your selections.")
    st.stop()

st.caption(f"Showing **{len(filtered):,}** ZIP codes after filters applied.")

# ── Analysis View Selector (persists across reruns) ─────────────────
view = st.radio(
    "Analysis view",
    options=[
        "Phase 1 — AGI Growth Analysis",
        "Phase 2 — IQRI (Income Quality Index)",
        "AI Risk Analyst",
    ],
    horizontal=True,
    label_visibility="collapsed",
    key="active_analysis_view",
)

if view == "Phase 1 — AGI Growth Analysis":
    render_phase1(filtered, trend_filtered, top_n)

elif view == "Phase 2 — IQRI (Income Quality Index)":
    render_phase2(filtered, trend_filtered, top_n)

else:
    render_ai_analyst(filtered, trend_filtered)
