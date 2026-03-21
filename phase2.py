import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils import COLORS, IQRI_COLORS, BASELINE_YEAR, LATEST_YEAR, ANALYSIS_YEARS


def render_phase2(df: pd.DataFrame, trend_df: pd.DataFrame, top_n: int) -> None:
    st.header("Phase 2 — Income Quality & Resilience Index (IQRI)")

    st.info(
        "**IQRI = (Business Income + Dividends) / Wages**  \n"
        "A higher IQRI indicates income less dependent on a single employer or industry.  \n"
        "- **Wage-Dependent (< 0.05):** High layoff risk — flag for conservative lending  \n"
        "- **Mixed (0.05–0.15):** Balanced income mix  \n"
        "- **Entrepreneurial (0.15–0.30):** Strong business ownership — commercial lending targets  \n"
        "- **Investment-Led (> 0.30):** Prime wealth management prospects"
    )

    valid = df.dropna(subset=["iqri", "agi_cagr", "iqri_tier"])

    agi_col = f"A00100_{LATEST_YEAR}"
    n1_col = f"N1_{LATEST_YEAR}"

    # ── KPI Row ──────────────────────────────────────────────────────
    tier_counts = valid["iqri_tier"].value_counts()
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("ZIP Codes w/ IQRI", f"{len(valid):,}")
    k2.metric("Wage-Dependent ZIPs", f"{tier_counts.get('Wage-Dependent', 0):,}")
    k3.metric("Entrepreneurial ZIPs", f"{tier_counts.get('Entrepreneurial', 0):,}")
    k4.metric("Investment-Led ZIPs", f"{tier_counts.get('Investment-Led', 0):,}")

    st.divider()

    # ── Scatter: IQRI vs AGI (bubble = population) ───────────────────
    st.subheader("IQRI vs. Total AGI — Wealth Management Target Map")
    st.caption(
        "Upper-right quadrant = high wealth + high income resilience → **prime wealth management targets**.  \n"
        "Bubble size = number of returns (population proxy). Log Y-scale."
    )

    scatter_df = valid.copy()
    scatter_df["zip_label"] = scatter_df["zipcode"] + " (" + scatter_df["STATE"] + ")"
    scatter_df["iqri_tier_str"] = scatter_df["iqri_tier"].astype(str)
    scatter_plot_df = scatter_df.copy()
    scatter_plot_df["iqri"] = scatter_plot_df["iqri"].clip(upper=3.0)

    fig_scatter = px.scatter(
        scatter_plot_df,
        x="iqri",
        y=agi_col,
        color="iqri_tier_str",
        color_discrete_map=IQRI_COLORS,
        size=n1_col,
        size_max=25,
        opacity=0.65,
        log_y=True,
        hover_name="zip_label",
        hover_data={
            "iqri": ":.3f",
            agi_col: ":,.0f",
            n1_col: ":,",
            "iqri_tier_str": True,
        },
        labels={
            "iqri": "IQRI Score",
            agi_col: f"Total AGI {LATEST_YEAR} ($000s)",
            "iqri_tier_str": "Income Tier",
            n1_col: "Returns",
        },
        category_orders={"iqri_tier_str": list(IQRI_COLORS.keys())},
    )

    for x_val, label in [(0.05, "0.05"), (0.15, "0.15"), (0.30, "0.30")]:
        fig_scatter.add_vline(x=x_val, line_dash="dot", line_color="gray", line_width=1)
        fig_scatter.add_annotation(
            x=x_val, y=0.02, yref="paper",
            text=label, showarrow=False,
            font=dict(size=10, color="gray"),
        )

    fig_scatter.update_layout(
        height=520,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="rgba(150,150,150,1)",
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.divider()

    # ── Top N ZIPs by IQRI  +  Risk-Opportunity Matrix ──────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"Top {top_n} ZIP Codes by IQRI")
        top_iqri = valid.nlargest(top_n, "iqri").copy()
        top_iqri["label"] = top_iqri["zipcode"] + " (" + top_iqri["STATE"] + ")"
        top_iqri["iqri_tier_str"] = top_iqri["iqri_tier"].astype(str)
        fig_bar = px.bar(
            top_iqri.sort_values("iqri"),
            x="iqri",
            y="label",
            orientation="h",
            color="iqri_tier_str",
            color_discrete_map=IQRI_COLORS,
            labels={"iqri": "IQRI Score", "label": "ZIP Code", "iqri_tier_str": "Tier"},
            hover_data={agi_col: ":,.0f", n1_col: ":,"},
            category_orders={"iqri_tier_str": list(IQRI_COLORS.keys())},
        )
        fig_bar.update_layout(
            height=max(400, top_n * 22),
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="rgba(150,150,150,1)",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.subheader("IQRI vs. AGI Growth — Risk-Opportunity Matrix")
        st.caption(
            "Upper-right: booming AND resilient income → best lending/WM prospects.  \n"
            "Lower-left: shrinking AND wage-dependent → avoid."
        )
        matrix_df = valid.copy()
        matrix_df["zip_label"] = matrix_df["zipcode"] + " (" + matrix_df["STATE"] + ")"
        matrix_df["iqri_tier_str"] = matrix_df["iqri_tier"].astype(str)
        matrix_plot_df = matrix_df.copy()
        matrix_plot_df["iqri"] = matrix_plot_df["iqri"].clip(upper=2.0)
        fig_matrix = px.scatter(
            matrix_plot_df,
            x="iqri",
            y="agi_cagr",
            color="iqri_tier_str",
            color_discrete_map=IQRI_COLORS,
            opacity=0.55,
            hover_name="zip_label",
            hover_data={"iqri": ":.3f", "agi_cagr": ":.2f", n1_col: ":,"},
            labels={
                "iqri": "IQRI Score",
                "agi_cagr": f"AGI CAGR % ({BASELINE_YEAR}→{LATEST_YEAR})",
                "iqri_tier_str": "Tier",
            },
            category_orders={"iqri_tier_str": list(IQRI_COLORS.keys())},
        )
        fig_matrix.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
        fig_matrix.add_vline(x=0.15, line_dash="dash", line_color="gray", line_width=1)
        fig_matrix.update_layout(
            height=max(400, top_n * 22),
            margin=dict(l=10, r=10, t=30, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="rgba(150,150,150,1)",
        )
        st.plotly_chart(fig_matrix, use_container_width=True)

    st.divider()

    # ── NEW: IQRI Trend Over Time (multi-year) ──────────────────────
    st.subheader(f"Income Resilience Trend ({BASELINE_YEAR}–{LATEST_YEAR})")
    st.caption(
        "Year-over-year median IQRI by state. A rising trend means income is diversifying "
        "away from wages — good for lending resilience."
    )

    # Calculate IQRI per state per year from trend data
    state_year_iqri = (
        trend_df.groupby(["STATE", "year"])
        .agg(
            total_wages=("wages", "sum"),
            total_biz=("business_inc", "sum"),
            total_div=("dividends", "sum"),
        )
        .reset_index()
    )
    state_year_iqri["iqri"] = (
        (state_year_iqri["total_biz"] + state_year_iqri["total_div"])
        / state_year_iqri["total_wages"].replace(0, float("nan"))
    )

    fig_iqri_trend = px.line(
        state_year_iqri.dropna(subset=["iqri"]),
        x="year",
        y="iqri",
        color="STATE",
        labels={"iqri": "IQRI (state-level)", "year": "Tax Year", "STATE": "State"},
    )
    fig_iqri_trend.update_layout(
        height=450,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="rgba(150,150,150,1)",
        xaxis=dict(dtick=1),
    )
    st.plotly_chart(fig_iqri_trend, use_container_width=True)

    st.divider()

    # ── State-Level IQRI Choropleth ──────────────────────────────────
    st.subheader("Median IQRI by State — Income Resilience Heatmap")
    state_iqri = (
        valid.groupby("STATE")
        .agg(median_iqri=("iqri", "median"), zip_count=("zipcode", "count"))
        .reset_index()
    )
    fig_map = px.choropleth(
        state_iqri,
        locations="STATE",
        locationmode="USA-states",
        color="median_iqri",
        scope="usa",
        color_continuous_scale=["#B02020", "#C9A84C", COLORS["primary"]],
        hover_data={"median_iqri": ":.3f", "zip_count": True},
        labels={"median_iqri": "Median IQRI", "zip_count": "ZIP Count"},
        title=f"Median IQRI by State ({LATEST_YEAR}) — Higher = More Entrepreneurial/Investment Income",
    )
    fig_map.update_layout(
        height=450,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        font_color="rgba(150,150,150,1)",
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # ── Tier Distribution Pie ────────────────────────────────────────
    st.subheader("Income Tier Distribution")
    tier_df = valid["iqri_tier"].value_counts().reset_index()
    tier_df.columns = ["Tier", "Count"]
    tier_df["Tier"] = tier_df["Tier"].astype(str)
    fig_pie = px.pie(
        tier_df,
        names="Tier",
        values="Count",
        color="Tier",
        color_discrete_map=IQRI_COLORS,
        hole=0.4,
    )
    fig_pie.update_layout(
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="rgba(150,150,150,1)",
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # ── Raw Data Table ───────────────────────────────────────────────
    with st.expander("View IQRI Data Table"):
        display_cols = [
            "zipcode", "STATE", "iqri", "iqri_tier", agi_col,
            f"A00200_{LATEST_YEAR}", f"A00900_{LATEST_YEAR}",
            f"A00600_{LATEST_YEAR}", n1_col,
        ]
        st.dataframe(
            valid[display_cols]
            .sort_values("iqri", ascending=False)
            .rename(columns={
                "iqri": "IQRI Score",
                "iqri_tier": "Tier",
                agi_col: f"AGI {LATEST_YEAR} ($000s)",
                f"A00200_{LATEST_YEAR}": "Wages ($000s)",
                f"A00900_{LATEST_YEAR}": "Business Inc. ($000s)",
                f"A00600_{LATEST_YEAR}": "Dividends ($000s)",
                n1_col: f"Returns {LATEST_YEAR}",
            }),
            use_container_width=True,
        )
