from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from charts import (
    chart_budget_vs_revenue,
    chart_vote_vs_budget,
    chart_popularity_vs_revenue,
    chart_genre_roi,
    chart_tag_count_relation,
    chart_country_language_heat,
    chart_country_language_facet_bar,
    chart_month_seasonality,
    chart_month_seasonality_heat,
    chart_decade_multi_trend,
    chart_sequel_original_bar,
    chart_vote_count_stability_line,
    chart_roi_profile_compare,
    chart_roi_profile_radar,
    chart_genre_country_heat,
    chart_runtime_vote_loess_facet,
    chart_budget_bin_roi_turning,
    chart_vote_hist,
    chart_year_trend,
    chart_runtime_box_by_genre,
    chart_corr_heatmap,
    chart_genre_share_by_decade,
    chart_country_roi,
    chart_company_roi,
)


def section_question_1(df: pd.DataFrame) -> None:
    st.subheader("Question 1: Do bigger budgets lead to higher revenue/ratings?")
    st.markdown(
        "- View A: Budget vs Revenue\n"
        "- View B: Budget vs Rating\n"
        "- View C: Popularity vs Revenue\n"
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("View A: Budget vs Revenue")
        has_a = df[["budget_clip", "revenue_clip"]].dropna().shape[0] > 0
        use_df_a = df if has_a else st.session_state.get("df_full", df)
        if not has_a:
            st.warning("No plottable data under current filters. Using full dataset for View A as a fallback.")
        corr_a = (
            use_df_a[["budget_clip", "revenue_clip"]].corr().iloc[0, 1]
            if use_df_a.shape[0]
            else np.nan
        )
        st.caption(f"Correlation: Budget-Revenue = {corr_a:.2f}")
        st.altair_chart(chart_budget_vs_revenue(use_df_a), use_container_width=True)

    with col_b:
        st.markdown("View B: Budget vs Rating")
        sub_b = df.dropna(subset=["budget_clip", "vote_average"]).query("budget_clip > 0")
        has_b = sub_b.shape[0] > 0
        use_df_b = df if has_b else st.session_state.get("df_full", df)
        use_sub_b = (
            use_df_b.dropna(subset=["budget_clip", "vote_average"]).query("budget_clip > 0")
            if use_df_b is not None
            else sub_b
        )
        if not has_b:
            st.warning("No plottable data under current filters. Using full dataset for View B as a fallback.")
        corr_b = (
            np.corrcoef(np.log1p(use_sub_b["budget_clip"]), use_sub_b["vote_average"])[0, 1]
            if use_sub_b.shape[0]
            else np.nan
        )
        st.caption(f"Correlation: ln(Budget)-Rating = {corr_b:.2f}")
        st.altair_chart(chart_vote_vs_budget(use_df_b), use_container_width=True)

    with st.expander("View C: Popularity vs Revenue", expanded=False):
        sub_c = df.dropna(subset=["popularity", "revenue_clip"]) if df.shape[0] else df
        if sub_c.shape[0] == 0:
            st.info("Insufficient popularity/revenue data under current filters. Consider broadening your filters.")
        else:
            corr_c = sub_c[["popularity", "revenue_clip"]].corr().iloc[0, 1]
            st.caption(f"Correlation: Popularity-Revenue = {corr_c:.2f}")
            st.altair_chart(chart_popularity_vs_revenue(df), use_container_width=True)


def section_question_2(df: pd.DataFrame) -> None:
    st.subheader("Question 2: Which genres have higher ROI?")
    st.markdown("- View: Median ROI by genre ranking")
    topk = st.slider("TopK", 5, 30, 10, key="k_roi")
    st.altair_chart(chart_genre_roi(df, top_k=topk), use_container_width=True)

    exploded = df.explode("genres_list")
    grp = (
        exploded.groupby("genres_list", dropna=True)
        .agg(median_roi=("roi", "median"), n=("id", "count"))
        .reset_index()
        .dropna(subset=["genres_list"])
    )
    if not grp.empty:
        best = grp.sort_values("median_roi", ascending=False).iloc[0]
        st.success(
            f"Top genre: {best['genres_list']} (Median ROI={best['median_roi']:.2f}, Samples={int(best['n'])})"
        )


def section_questions_hub(df: pd.DataFrame) -> None:
    st.subheader("Question Hub")

    opt = st.selectbox(
        "Choose an example chart:",
        (
            "Runtime vs Rating",
            "Tag count vs Rating",
            "Country × Language × ROI (Heatmap)",
            "Country × Language × ROI (Facet Bar)",
            "Release month vs Revenue and Rating",
            "Release month heatmap",
            "Decade trends: Budget/Revenue/Rating",
            "Sequel vs Original Comparison",
        ),
    )

    if opt == "Runtime vs Rating":
        k = st.slider("Facet TopK (by genre)", 2, 8, 4)
        st.altair_chart(chart_runtime_vote_loess_facet(df, top_k=k), use_container_width=True)
    elif opt == "Tag count vs Rating":
        st.altair_chart(chart_tag_count_relation(df, target="vote"), use_container_width=True)
    elif opt == "Country × Language × ROI (Heatmap)":
        metric = st.selectbox("Metric", ("roi", "revenue"), index=0, format_func=lambda x: "ROI" if x == "roi" else "Revenue")
        st.altair_chart(chart_country_language_heat(df, metric=metric), use_container_width=True)
    elif opt == "Country × Language × ROI (Facet Bar)":
        metric = st.selectbox("Metric", ("roi", "revenue"), index=0, format_func=lambda x: "ROI" if x == "roi" else "Revenue", key="metric_facet")
        st.altair_chart(chart_country_language_facet_bar(df, metric=metric), use_container_width=True)
    elif opt == "Release month vs Revenue and Rating":
        st.altair_chart(chart_month_seasonality(df), use_container_width=True)
    elif opt == "Release month heatmap":
        metric = st.selectbox("Metric", ("revenue", "vote_average"), index=0, format_func=lambda x: "Revenue" if x == "revenue" else "Rating")
        st.altair_chart(chart_month_seasonality_heat(df, metric=metric), use_container_width=True)
    elif opt == "Decade trends: Budget/Revenue/Rating":
        st.altair_chart(chart_decade_multi_trend(df), use_container_width=True)
    elif opt == "Sequel vs Original Comparison":
        st.altair_chart(chart_sequel_original_bar(df, metric="roi"), use_container_width=True)



def section_eda(df: pd.DataFrame) -> None:
    st.subheader("Exploratory Data Analysis")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("Rating distribution")
        st.altair_chart(chart_vote_hist(df), use_container_width=True)
    with c2:
        st.markdown("Yearly trend: average rating vs average popularity")
        st.altair_chart(chart_year_trend(df), use_container_width=True)

    st.markdown("---")
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("Runtime distribution of popular genres (boxplot)")
        st.altair_chart(chart_runtime_box_by_genre(df), use_container_width=True)
    with c4:
        st.markdown("Feature correlation heatmap")
        st.altair_chart(chart_corr_heatmap(df), use_container_width=True)


def section_leaderboard(df: pd.DataFrame) -> None:
    st.subheader("Leaderboard")
    metric = st.selectbox("Sort by", ["revenue", "roi"], format_func=lambda x: "Revenue" if x == "revenue" else "ROI")
    top_k = st.slider("Top N", 5, 50, 20)
    cols = [c for c in ["title", "release_year", "budget", "revenue", "profit", "roi", "vote_average", "vote_count"] if c in df.columns]
    data = df.dropna(subset=[metric]).sort_values(metric, ascending=False).head(top_k)
    st.dataframe(
        data[cols].style.format({
            "budget": "${:,.0f}", "revenue": "${:,.0f}", "profit": "${:,.0f}", "roi": "{:.2f}", "vote_average": "{:.1f}"
        }),
        use_container_width=True,
    )
