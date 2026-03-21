import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils import COLORS, DIVERGING_SCALE, BASELINE_YEAR, LATEST_YEAR, ANALYSIS_YEARS


def render_phase1(df: pd.DataFrame, trend_df: pd.DataFrame, top_n: int) -> None:
    st.header("Phase 1 — AGI Growth: Wealth Exodus vs. Booming ZIPs")
    st.markdown(
        f"Comparing **{BASELINE_YEAR} vs. {LATEST_YEAR}** Adjusted Gross Income (AGI) by ZIP code.  \n"
        f"Growth measured as **5-year CAGR** (Compound Annual Growth Rate) to avoid single-year flukes."
    )

    # ── KPI Row ──────────────────────────────────────────────────────
    valid = df.dropna(subset=["agi_cagr"])
    total = len(valid)
    booming = (valid["agi_cagr"] > 4).sum()
    shrinking = (valid["agi_cagr"] < 0).sum()
    median_cagr = valid["agi_cagr"].median()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("ZIP Codes Analyzed", f"{total:,}")
    k2.metric("Booming (>4% CAGR)", f"{booming:,}", f"{booming/total*100:.1f}%")
    k3.metric("Shrinking (<0% CAGR)", f"{shrinking:,}", f"-{shrinking/total*100:.1f}%", delta_color="inverse")
    k4.metric("Median CAGR", f"{median_cagr:.2f}%")

    st.divider()

    # ── Bar Charts: Top Gainers and Losers ───────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"Top {top_n} Booming ZIP Codes (CAGR)")
        gainers = valid.nlargest(top_n, "agi_cagr").copy()
        gainers["label"] = gainers["zipcode"] + " (" + gainers["STATE"] + ")"
        fig_gain = px.bar(
            gainers.sort_values("agi_cagr"),
            x="agi_cagr",
            y="label",
            orientation="h",
            color="agi_cagr",
            color_continuous_scale=[[0, "#70C070"], [1, COLORS["gain"]]],
            labels={"agi_cagr": "AGI CAGR %", "label": "ZIP Code"},
        )
        fig_gain.update_layout(
            coloraxis_showscale=False,
            height=max(400, top_n * 22),
            margin=dict(l=10, r=10, t=30, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="rgba(150,150,150,1)",
        )
        fig_gain.update_traces(
            hovertemplate="<b>%{y}</b><br>CAGR: %{x:.2f}%<extra></extra>"
        )
        st.plotly_chart(fig_gain, use_container_width=True)

    with col2:
        st.subheader(f"Top {top_n} Shrinking ZIP Codes (CAGR)")
        losers = valid.nsmallest(top_n, "agi_cagr").copy()
        losers["label"] = losers["zipcode"] + " (" + losers["STATE"] + ")"
        fig_loss = px.bar(
            losers.sort_values("agi_cagr", ascending=False),
            x="agi_cagr",
            y="label",
            orientation="h",
            color="agi_cagr",
            color_continuous_scale=[[0, COLORS["loss"]], [1, "#E07070"]],
            labels={"agi_cagr": "AGI CAGR %", "label": "ZIP Code"},
        )
        fig_loss.update_layout(
            coloraxis_showscale=False,
            height=max(400, top_n * 22),
            margin=dict(l=10, r=10, t=30, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="rgba(150,150,150,1)",
        )
        fig_loss.update_traces(
            hovertemplate="<b>%{y}</b><br>CAGR: %{x:.2f}%<extra></extra>"
        )
        st.plotly_chart(fig_loss, use_container_width=True)

    st.divider()

    # ── NEW: Year-over-Year AGI Trend (multi-year) ───────────────────
    st.subheader(f"AGI Trend by State ({BASELINE_YEAR}–{LATEST_YEAR})")
    st.caption(
        "Year-over-year total AGI by state confirms whether growth is sustained or a one-year fluke. "
        "Select specific states in the sidebar to zoom in."
    )

    state_trend = (
        trend_df.groupby(["STATE", "year"])
        .agg(total_agi=("agi", "sum"))
        .reset_index()
    )
    # Normalize to baseline year = 100 for fair comparison across states
    baseline_agi = state_trend[state_trend["year"] == BASELINE_YEAR][["STATE", "total_agi"]].rename(
        columns={"total_agi": "base_agi"}
    )
    state_trend = state_trend.merge(baseline_agi, on="STATE", how="left")
    state_trend["indexed_agi"] = (state_trend["total_agi"] / state_trend["base_agi"]) * 100

    fig_trend = px.line(
        state_trend,
        x="year",
        y="indexed_agi",
        color="STATE",
        labels={"indexed_agi": f"AGI Index ({BASELINE_YEAR}=100)", "year": "Tax Year", "STATE": "State"},
        hover_data={"total_agi": ":,.0f"},
    )
    fig_trend.add_hline(y=100, line_dash="dash", line_color="gray", line_width=1,
                        annotation_text="No Growth Baseline")
    fig_trend.update_layout(
        height=480,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="rgba(150,150,150,1)",
        xaxis=dict(dtick=1),
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    st.divider()

    # ── Scatter: AGI Baseline vs Latest ──────────────────────────────
    st.subheader(f"AGI {BASELINE_YEAR} vs. {LATEST_YEAR} — All Filtered ZIP Codes")
    st.caption(
        "Points above the dashed line grew over the 5-year window. Color = CAGR. "
        "Log scale accommodates the wide AGI range."
    )

    agi_base_col = f"A00100_{BASELINE_YEAR}"
    agi_latest_col = f"A00100_{LATEST_YEAR}"

    scatter_df = valid.copy()
    scatter_df["zip_label"] = scatter_df["zipcode"] + " (" + scatter_df["STATE"] + ")"

    fig_scatter = px.scatter(
        scatter_df,
        x=agi_base_col,
        y=agi_latest_col,
        color="agi_cagr",
        color_continuous_scale=DIVERGING_SCALE,
        color_continuous_midpoint=0,
        opacity=0.55,
        log_x=True,
        log_y=True,
        hover_name="zip_label",
        hover_data={
            "agi_cagr": ":.2f",
            "agi_total_growth_pct": ":.1f",
            agi_base_col: ":,.0f",
            agi_latest_col: ":,.0f",
        },
        labels={
            agi_base_col: f"AGI {BASELINE_YEAR} ($000s)",
            agi_latest_col: f"AGI {LATEST_YEAR} ($000s)",
            "agi_cagr": "CAGR %",
        },
    )

    # y = x reference line
    min_val = max(scatter_df[[agi_base_col, agi_latest_col]].min().min(), 1)
    max_val = scatter_df[[agi_base_col, agi_latest_col]].max().max()
    fig_scatter.add_trace(
        go.Scatter(
            x=[min_val, max_val], y=[min_val, max_val],
            mode="lines",
            line=dict(color="gray", dash="dash", width=1),
            name="No Growth Baseline", showlegend=True,
        )
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

    # ── State-Level Choropleth ───────────────────────────────────────
    st.subheader("State-Level AGI Growth Map (CAGR)")
    state_agg = (
        valid.groupby("STATE")
        .agg(median_cagr=("agi_cagr", "median"), zip_count=("zipcode", "count"))
        .reset_index()
    )
    fig_map = px.choropleth(
        state_agg,
        locations="STATE",
        locationmode="USA-states",
        color="median_cagr",
        scope="usa",
        color_continuous_scale=DIVERGING_SCALE,
        color_continuous_midpoint=0,
        hover_data={"median_cagr": ":.2f", "zip_count": True},
        labels={"median_cagr": "Median AGI CAGR %", "zip_count": "ZIP Codes"},
        title=f"Median AGI CAGR by State ({BASELINE_YEAR} → {LATEST_YEAR})",
    )
    fig_map.update_layout(
        height=450,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        font_color="rgba(150,150,150,1)",
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # ── Raw Data Table ───────────────────────────────────────────────
    with st.expander("View Raw Data Table"):
        display_cols = [
            "zipcode", "STATE",
            agi_base_col, agi_latest_col,
            "agi_cagr", "agi_total_growth_pct",
            f"N1_{LATEST_YEAR}", "status",
        ]
        st.dataframe(
            valid[display_cols]
            .sort_values("agi_cagr", ascending=False)
            .rename(columns={
                agi_base_col: f"AGI {BASELINE_YEAR} ($000s)",
                agi_latest_col: f"AGI {LATEST_YEAR} ($000s)",
                "agi_cagr": "CAGR %",
                "agi_total_growth_pct": "Total Growth %",
                f"N1_{LATEST_YEAR}": f"Returns {LATEST_YEAR}",
            }),
            use_container_width=True,
        )
